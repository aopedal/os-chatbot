from typing import List, Dict
from datetime import datetime, timezone
import httpx
import tiktoken
import logging
import utils.config as config

logger = logging.getLogger("retrieval")

ENC = tiktoken.encoding_for_model("gpt-4o")


def count_tokens(text: str) -> int:
    return len(ENC.encode(text))


class ConversationMemoryStore:
    def __init__(self):
        self.messages: Dict[str, List[Dict]] = {}
        self.summaries: Dict[str, str] = {}
        self.last_sources: Dict[str, List[Dict]] = {}

    async def append_message(self, user_id: str, role: str, content: str):
        self.messages.setdefault(user_id, [])
        self.messages[user_id].append({
            "role": role,
            "content": content,
            "time": datetime.now(timezone.utc).isoformat()
        })

    async def get_recent_messages(self, user_id: str):
        return self.messages.get(user_id, [])

    async def get_summary(self, user_id: str) -> str:
        return self.summaries.get(user_id, "")

    async def update_summary(self, user_id: str, summary: str):
        self.summaries[user_id] = summary

    async def store_sources(self, user_id: str, sources: List[Dict]):
        self.last_sources[user_id] = sources

    async def get_sources(self, user_id: str) -> List[Dict]:
        return self.last_sources.get(user_id, [])


class ConversationMemoryManager:
    def __init__(
        self,
        store: ConversationMemoryStore,
        recent_turns: int = 10,
        summary_max_tokens: int = 800,
        recent_max_tokens: int = 1500
    ):
        self.store = store
        self.recent_turns = recent_turns
        self.summary_max_tokens = summary_max_tokens
        self.recent_max_tokens = recent_max_tokens

    async def _get_recent_messages_budgeted(self, user_id: str) -> List[Dict]:
        msgs = await self.store.get_recent_messages(user_id)
        collected = []
        token_count = 0

        for m in reversed(msgs):
            t = count_tokens(m["content"])
            if token_count + t > self.recent_max_tokens:
                break
            collected.insert(0, m)
            token_count += t
            if len(collected) >= self.recent_turns:
                break

        logger.info(
            f"Recent memory: {len(collected)} messages, "
            f"{token_count} tokens"
        )

        return collected

    async def build_messages(self, user_id: str) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = []

        summary = await self.store.get_summary(user_id)
        if summary:
            messages.append({
                "role": "system",
                "content": (
                    "KOMPRIMERT SAMTALEHISTORIKK (autorativ):\n\n"
                    f"{summary}"
                )
            })
            logger.info(
                f"Summary tokens: {count_tokens(summary)}"
            )

        recent = await self._get_recent_messages_budgeted(user_id)
        for m in recent:
            messages.append({
                "role": m["role"],
                "content": m["content"]
            })

        return messages

    async def update(
        self,
        user_id: str,
        user_msg: str,
        assistant_msg: str,
        sources: List[Dict]
    ):
        # Store raw messages
        await self.store.append_message(user_id, "user", user_msg)
        await self.store.append_message(user_id, "assistant", assistant_msg)
        await self.store.store_sources(user_id, sources)

        old_summary = await self.store.get_summary(user_id)

        source_refs = [
            f"{s.get('type')}:{s.get('identifier')}"
            for s in sources
        ]

        prompt = (
            "Du vedlikeholder et løpende, konsist sammendrag av en samtale.\n\n"
            "Eksisterende sammendrag:\n"
            f"{old_summary or '(ingen)'}\n\n"
            "Ny dialog:\n"
            f"Bruker: {user_msg}\n"
            f"Assistent: {assistant_msg}\n\n"
            "Kilder brukt i svaret:\n"
            f"{', '.join(source_refs) if source_refs else 'Ingen'}\n\n"
            "Oppdater sammendraget slik at:\n"
            "- Viktige fakta, beslutninger og forklaringer bevares\n"
            "- Eventuelle kilder som er brukt nevnes på høyt nivå\n"
            "- Småprat og detaljer fjernes\n"
            "- Sammendraget forblir kort og presist"
        )

        async with httpx.AsyncClient(timeout=None) as client:
            resp = await client.post(
                f"{config.LLM_BASE}/chat/completions",
                json={
                    "model": "gpt-oss-20b",
                    "messages": [
                        {"role": "system", "content": "Du oppsummerer samtaler."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 300,
                    "temperature": 0
                }
            )

            data = resp.json()
            new_summary = data["choices"][0]["message"]["content"]

        logger.info(
            f"New summary tokens: {count_tokens(new_summary)}"
        )

        # Hard safety cap
        while count_tokens(new_summary) > self.summary_max_tokens:
            new_summary = "\n".join(new_summary.split("\n")[1:])

        await self.store.update_summary(user_id, new_summary)

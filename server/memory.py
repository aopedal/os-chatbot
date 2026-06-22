from datetime import UTC, datetime

import httpx
import tiktoken

ENC = tiktoken.encoding_for_model("gpt-4o")

SUMMARY_MAX_WORDS = 300
SUMMARY_SYSTEM_PROMPT = (
    "Du oppdaterer et løpende sammendrag av en samtale om operativsystemer. "
    "Flett inn den nye turen i sammendraget. "
    "Behold viktige faglige begreper, spørsmål og svar. "
    f"Hold sammendraget under {SUMMARY_MAX_WORDS} ord. "
    "Returner kun det oppdaterte sammendraget, ingen forklaring."
)


def count_tokens(text: str) -> int:
    return len(ENC.encode(text))


class ConversationMemoryStore:
    def __init__(self):
        self.messages: dict[str, list[dict[str, str]]] = {}
        self.summaries: dict[str, str] = {}

    async def append_message(self, user_id: str, role: str, content: str):
        self.messages.setdefault(user_id, [])
        self.messages[user_id].append({
            "role": role,
            "content": content,
            "time": datetime.now(UTC).isoformat(),
        })

    async def get_recent_turns(self, user_id: str, turns: int) -> list[dict[str, str]]:
        """Return the last `turns` complete user/assistant pairs."""
        msgs = self.messages.get(user_id, [])
        if not msgs:
            return []
        # Walk backwards collecting complete pairs
        pairs: list[tuple[dict, dict]] = []
        i = len(msgs) - 1
        while i >= 1 and len(pairs) < turns:
            if msgs[i]["role"] == "assistant" and msgs[i - 1]["role"] == "user":
                pairs.append((msgs[i - 1], msgs[i]))
                i -= 2
            else:
                i -= 1
        # Reverse so chronological order is preserved
        result = []
        for user_msg, assistant_msg in reversed(pairs):
            result.append(user_msg)
            result.append(assistant_msg)
        return result

    async def get_summary(self, user_id: str) -> str:
        return self.summaries.get(user_id, "")

    async def update_summary(self, user_id: str, new_summary: str):
        self.summaries[user_id] = new_summary


class ConversationMemoryManager:
    def __init__(
        self,
        store: ConversationMemoryStore,
        recent_turns: int = 3,
        memory_max_tokens: int = 6000,
    ):
        self.store = store
        self.recent_turns = recent_turns
        self.memory_max_tokens = memory_max_tokens

    async def build_messages(self, user_id: str) -> list[dict[str, str]]:
        """
        Build structured chat messages for the LLM:
        - summary injected as a system message (if present)
        - last `recent_turns` complete user/assistant pairs as real roles
        """
        messages: list[dict[str, str]] = []

        summary = await self.store.get_summary(user_id)
        if summary:
            messages.append({
                "role": "system",
                "content": f"Sammendrag av samtalen så langt:\n{summary}",
            })

        recent = await self.store.get_recent_turns(user_id, self.recent_turns)
        for m in recent:
            messages.append({"role": m["role"], "content": m["content"]})

        return messages

    async def update(
        self,
        user_id: str,
        user_msg: str,
        assistant_msg: str,
        llm_base: str,
        model: str,
    ):
        """Append the new turn and update the running summary via the LLM."""
        await self.store.append_message(user_id, "user", user_msg)
        await self.store.append_message(user_id, "assistant", assistant_msg)
        await self._update_summary(user_id, user_msg, assistant_msg, llm_base, model)

    async def _update_summary(
        self,
        user_id: str,
        user_msg: str,
        assistant_msg: str,
        llm_base: str,
        model: str,
    ):
        existing_summary = await self.store.get_summary(user_id)
        prompt_content = (
            f"Eksisterende sammendrag:\n{existing_summary}\n\n"
            if existing_summary
            else ""
        )
        prompt_content += (
            f"Ny tur:\n"
            f"Student: {user_msg}\n"
            f"Assistent: {assistant_msg}"
        )
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{llm_base}/chat/completions",
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                            {"role": "user", "content": prompt_content},
                        ],
                        "max_tokens": 512,
                        "temperature": 0,
                    },
                )
                resp.raise_for_status()
                new_summary = (
                    resp.json()["choices"][0]["message"]["content"].strip()
                )
            await self.store.update_summary(user_id, new_summary)
        except Exception:
            # Summary update is best-effort; never block or crash the request
            pass
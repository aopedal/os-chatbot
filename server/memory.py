from typing import List, Dict
from datetime import datetime
import tiktoken

ENC = tiktoken.encoding_for_model("gpt-4o")

def count_tokens(text: str) -> int:
    return len(ENC.encode(text))


class ConversationMemoryStore:
    def __init__(self):
        self.messages: Dict[str, List[Dict]] = {}
        self.summaries: Dict[str, str] = {}

    async def append_message(self, user_id: str, role: str, content: str):
        self.messages.setdefault(user_id, [])
        self.messages[user_id].append({
            "role": role,
            "content": content,
            "time": datetime.utcnow().isoformat()
        })

    async def get_recent_messages(self, user_id: str, limit: int):
        msgs = self.messages.get(user_id, [])
        return msgs[-limit:] if msgs else []

    async def get_summary(self, user_id: str) -> str:
        return self.summaries.get(user_id, "")

    async def update_summary(self, user_id: str, new_summary: str):
        self.summaries[user_id] = new_summary


class ConversationMemoryManager:
    def __init__(self, store: ConversationMemoryStore, recent_turns: int = 3, memory_max_tokens: int = 6000):
        self.store = store
        self.recent_turns = recent_turns
        self.memory_max_tokens = memory_max_tokens

    async def build_memory_block(self, user_id: str) -> str:
        summary = await self.store.get_summary(user_id)
        recent = await self.store.get_recent_messages(user_id, self.recent_turns)

        block = ""
        if summary:
            block += f"SAMMENDRAG AV SAMTALE:\n{summary}\n\n"

        if recent:
            block += "SISTE MELDINGER:\n"
            for m in recent:
                block += f"{m['role'].capitalize()}: {m['content']}\n"

        return block
    
    async def build_messages(self, user_id: str) -> List[Dict[str, str]]:
        """
        Build structured chat messages for the LLM:
        - summary as system
        - recent turns as real user/assistant roles
        """
        messages: List[Dict[str, str]] = []

        summary = await self.store.get_summary(user_id)
        if summary:
            messages.append({
                "role": "system",
                "content": f"Conversation summary:\n{summary}"
            })

        recent = await self.store.get_recent_messages(user_id, self.recent_turns)
        for m in recent:
            messages.append({
                "role": m["role"],
                "content": m["content"]
            })

        return messages

    async def update(self, user_id: str, user_msg: str, assistant_msg: str):
        await self.store.append_message(user_id, "user", user_msg)
        await self.store.append_message(user_id, "assistant", assistant_msg)

        summary = await self.store.get_summary(user_id)
        summary += f"\nBruker spurte: {user_msg}"

        while count_tokens(summary) > self.memory_max_tokens:
            summary = "\n".join(summary.split("\n")[1:])

        await self.store.update_summary(user_id, summary)
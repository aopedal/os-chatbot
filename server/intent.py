import logging
from enum import StrEnum
from typing import TypedDict

import httpx
import settings

logger = logging.getLogger("server.intent")


class IntentCategory(StrEnum):
    RECALL = "RECALL"
    CONCEPTUAL = "CONCEPTUAL"
    COMPARISON = "COMPARISON"
    SYNTHESIS = "SYNTHESIS"
    DEBUGGING = "DEBUGGING"
    PROCEDURE = "PROCEDURE"
    VERIFICATION = "VERIFICATION"
    NAVIGATIONAL = "NAVIGATIONAL"


class IntentResult(TypedDict):
    category: str
    wants_direct_answer: bool
    fallback: bool  # True when classification failed and defaults were used
    raw_response: str


_FALLBACK: IntentResult = {
    "category": "RECALL",
    "wants_direct_answer": False,
    "fallback": True,
    "raw_response": "",
}


def _parse_response(raw: str) -> tuple[str, bool] | None:
    upper = raw.strip().upper()
    for label in IntentCategory.__members__:
        if label in upper:
            return label, "DIRECT" in upper
    return None


async def classify_intent(message: str, model: str, llm_base: str) -> IntentResult:
    raw = ""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{llm_base}/chat/completions",
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": settings.get(
                                "intent_classifier_prompt", ""
                            ).format(question=message),
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.1,
                },
            )
            response.raise_for_status()
            raw = (response.json()["choices"][0]["message"]["content"] or "").strip()

        result = _parse_response(raw)
        if result is None:
            logger.warning(
                f"Could not extract intent from response: {raw!r}, falling back"
            )
            return {**_FALLBACK, "raw_response": raw}
        category, wants_direct = result
        return {
            "category": category,
            "wants_direct_answer": wants_direct,
            "fallback": False,
            "raw_response": raw,
        }

    except Exception as e:
        logger.warning(
            f"Intent classification failed ({type(e).__name__}: {e}), "
            f"falling back to direct mode"
        )
        return {**_FALLBACK, "raw_response": raw}

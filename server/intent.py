import logging
from typing import TypedDict

import httpx
import settings

logger = logging.getLogger("server.intent")


class IntentResult(TypedDict):
    category: str
    wants_direct_answer: bool
    fallback: bool  # True when classification failed and defaults were used
    raw_response: str


def _parse_response(raw: str, valid_names: list[str]) -> tuple[str, bool] | None:
    upper = raw.strip().upper()
    for label in valid_names:
        if label.upper() in upper:
            return label, "DIRECT" in upper
    return None


async def classify_intent(message: str, model: str, llm_base: str) -> IntentResult:
    raw = ""
    categories = settings.get("categories", [])
    valid_names = [cat["name"] for cat in categories]
    fallback_name = next(
        (cat["name"] for cat in categories if not cat.get("socratic", False)),
        valid_names[0] if valid_names else "RECALL",
    )
    categories_str = "\n".join(
        f"{cat['name']} – {cat['description']}" for cat in categories
    )
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
                            ).format(
                                categories=categories_str, question=message
                            ),
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.1,
                },
            )
            response.raise_for_status()
            raw = (response.json()["choices"][0]["message"]["content"] or "").strip()

        result = _parse_response(raw, valid_names)
        if result is None:
            logger.warning(
                f"Could not extract intent from response: {raw!r}, falling back"
            )
            return {
                "category": fallback_name,
                "wants_direct_answer": False,
                "fallback": True,
                "raw_response": raw,
            }
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
        return {
            "category": fallback_name,
            "wants_direct_answer": False,
            "fallback": True,
            "raw_response": raw,
        }

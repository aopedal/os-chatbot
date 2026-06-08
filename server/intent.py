import logging
from enum import StrEnum
from typing import TypedDict

import httpx

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

_CLASSIFIER_PROMPT = """\
Classify the student question below into exactly one category.

Categories:
RECALL – asks for a definition or fact
CONCEPTUAL – asks why or how something works
COMPARISON – asks about differences or tradeoffs
SYNTHESIS – an exercise, task, or design challenge
DEBUGGING – diagnosing a specific broken thing
PROCEDURE – asks for step-by-step instructions
VERIFICATION – asks whether something they did is correct
NAVIGATIONAL – asks about the curriculum or where to find something

If the student explicitly asks for a direct answer rather than hints \
(e.g. "just tell me", "bare gi meg svaret", "fortell meg direkte"), \
append DIRECT after the category name.

Examples:
What is a semaphore? → Category: RECALL
Why does deadlock happen? → Category: CONCEPTUAL
Just tell me the answer → Category: RECALL DIRECT

Student question: {question}
Category:"""


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
                            "content": _CLASSIFIER_PROMPT.format(question=message),
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

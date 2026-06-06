import json
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


_FALLBACK: IntentResult = {"category": "RECALL", "wants_direct_answer": False, "fallback": True}

_CLASSIFIER_PROMPT = (
    "Classify the following student question into exactly one of these categories:\n\n"
    "- RECALL: asks for a definition or fact\n"
    "- CONCEPTUAL: asks why or how something works\n"
    "- COMPARISON: asks about differences or tradeoffs between two or more things\n"
    "- SYNTHESIS: an exercise, task, or design challenge\n"
    "- DEBUGGING: diagnosing a specific broken thing\n"
    "- PROCEDURE: asks for step-by-step instructions\n"
    "- VERIFICATION: asks whether something they have done is correct\n"
    "- NAVIGATIONAL: asks about the curriculum or where to find something\n\n"
    "Also detect whether the student is explicitly requesting a direct answer or expressing "
    "frustration with guided responses "
    '(e.g. "just give me the answer", "stop with the hints", "tell me directly").\n\n'
    "Respond with only JSON in this exact format, no explanation:\n"
    '{{"category": "<LABEL>", "wants_direct_answer": <true|false>}}\n\n'
    "Question: {question}"
)


def _parse_response(raw: str) -> tuple[str, bool] | None:
    """Try JSON first, then scan for a bare category label. Returns (category, wants_direct) or None."""
    # Strip markdown code fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    # Strict JSON parse
    try:
        parsed = json.loads(raw)
        category = str(parsed.get("category", "")).upper()
        wants_direct = bool(parsed.get("wants_direct_answer", False))
        if category in IntentCategory.__members__:
            return category, wants_direct
        logger.warning(f"JSON parsed but unknown category {category!r}")
    except json.JSONDecodeError:
        logger.warning(f"Intent classifier returned non-JSON: {raw!r}, scanning for label")

    # Scan the raw text for any known label
    upper = raw.upper()
    for label in IntentCategory.__members__:
        if label in upper:
            wants_direct = "TRUE" in upper
            return label, wants_direct

    return None


async def classify_intent(message: str, model: str, llm_base: str) -> IntentResult:
    prompt = _CLASSIFIER_PROMPT.format(question=json.dumps(message))
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{llm_base}/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 100,
                    "temperature": 0.0,
                },
            )
            response.raise_for_status()
            raw = response.json()["choices"][0]["message"]["content"].strip()

        result = _parse_response(raw)
        if result is None:
            logger.warning(f"Could not extract intent from response: {raw!r}, falling back")
            return _FALLBACK
        category, wants_direct = result
        return {"category": category, "wants_direct_answer": wants_direct, "fallback": False}

    except Exception as e:
        logger.warning(f"Intent classification failed ({type(e).__name__}: {e}), falling back to direct mode")
        return _FALLBACK

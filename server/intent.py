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


_FALLBACK: IntentResult = {"category": "RECALL", "wants_direct_answer": False}

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
    '{"category": "<LABEL>", "wants_direct_answer": <true|false>}\n\n'
    "Question: {question}"
)


async def classify_intent(message: str, model: str, llm_base: str) -> IntentResult:
    prompt = _CLASSIFIER_PROMPT.format(question=json.dumps(message))
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{llm_base}/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 50,
                    "temperature": 0.0,
                },
            )
            response.raise_for_status()
            raw = response.json()["choices"][0]["message"]["content"].strip()

            # Strip markdown code fences if the model wraps the JSON
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            parsed = json.loads(raw)
            category = str(parsed.get("category", "")).upper()
            if category not in IntentCategory.__members__:
                logger.warning(f"Unknown intent category {category!r} from classifier, falling back")
                return _FALLBACK
            return {
                "category": category,
                "wants_direct_answer": bool(parsed.get("wants_direct_answer", False)),
            }

    except Exception as e:
        logger.warning(f"Intent classification failed ({type(e).__name__}: {e}), falling back to direct mode")
        return _FALLBACK

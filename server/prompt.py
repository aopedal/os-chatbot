from typing import Any

import settings
from collection_types import COLLECTION_TYPE_MAP
from intent import IntentResult


def socratic_mode_active(intent: IntentResult | None, socratic_mode: str) -> bool:
    if socratic_mode == "always":
        return True
    if socratic_mode == "auto":
        socratic_names = {
            cat["name"]
            for cat in settings.get("categories", [])
            if cat.get("socratic", False)
        }
        return (
            intent is not None
            and not intent.get("wants_direct_answer", False)
            and intent.get("category") in socratic_names
        )
    return False


def build_system_prompt(
    context: str, now: str, intent: IntentResult | None, socratic_mode: str
) -> str:
    intro_key = (
        "socratic_intro"
        if socratic_mode_active(intent, socratic_mode)
        else "direct_intro"
    )
    return (
        settings.get(intro_key, "")
        + "\n\n"
        + settings.get("shared_instructions", "").format(now=now, context=context)
    )


def build_context_docs(
    payloads: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str]:
    sources = []
    context_blocks = []

    for payload in payloads:
        type_id = payload.get("type") or ""
        collection_type = COLLECTION_TYPE_MAP.get(type_id)
        if collection_type is None:
            raise ValueError(f"Unknown collection type: {type_id!r}")

        identifier, url, text = collection_type.extract_source(payload)

        sources.append({
            "type": type_id,
            "identifier": identifier,
            "url": url,
            "text": text,
        })
        context_blocks.append(
            f"Kildereferanse: {identifier}\nURL: {url}\nTekst:\n{text}"
        )

    return sources, "\n\n---\n\n".join(context_blocks)

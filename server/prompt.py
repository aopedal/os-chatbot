from typing import Any

import settings
from collection_types import COLLECTION_TYPE_MAP

_SYSTEM_PROMPT_FOOTER = (
    "Du har en pågående samtale med brukeren. "
    "Samtalehistorikk er vedlagt og skal brukes hvis relevant.\n"
    "Nåværende tidspunkt: {now}\n\n"
    "---\n\n"
    "RELEVANT PENSUMMATERIALE:\n\n"
    "{context}"
)


def socratic_mode_active(intent: dict | None, socratic_mode: bool) -> bool:
    categories = set(settings.get("socratic_categories", []))
    return (
        socratic_mode
        and intent is not None
        and not intent.get("wants_direct_answer", False)
        and intent.get("category") in categories
    )


def build_system_prompt(
    context: str, now: str, intent: dict | None, socratic_mode: bool
) -> str:
    intro_key = (
        "socratic_intro"
        if socratic_mode_active(intent, socratic_mode)
        else "direct_intro"
    )
    return (
        settings.get(intro_key, "")
        + "\n\n"
        + settings.get("shared_instructions", "")
        + "\n\n"
        + _SYSTEM_PROMPT_FOOTER.format(now=now, context=context)
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

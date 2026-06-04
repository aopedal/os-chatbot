from typing import Any

from collection_types import COLLECTION_TYPE_MAP


def build_context_docs(payloads: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], str]:
    sources = []
    context_blocks = []

    for payload in payloads:
        type_id = payload.get("type") or ""
        collection_type = COLLECTION_TYPE_MAP.get(type_id)
        if collection_type is None:
            raise ValueError(f"Unknown collection type: {type_id!r}")

        identifier, url, text = collection_type.extract_source(payload)

        sources.append({"type": type_id, "identifier": identifier, "url": url, "text": text})
        context_blocks.append(f"Kildereferanse: {identifier}\nURL: {url}\nTekst:\n{text}")

    return sources, "\n\n---\n\n".join(context_blocks)

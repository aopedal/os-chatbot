import re


def to_qdrant_name(model_name: str) -> str:
    name = model_name.lower()
    name = re.sub(r"[^a-z0-9\-_]+", "-", name)
    name = re.sub(r"-+", "-", name).strip("-_")
    return name


def to_weaviate_class(model_name: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", model_name)
    parts = [p.capitalize() for p in parts if p]
    name = "".join(parts)
    if not name:
        name = "Model"
    elif not name[0].isalpha():
        name = "M" + name
    return name

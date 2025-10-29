import re

def to_qdrant_name(model_name: str) -> str:
    """
    Converts a model name into a valid Qdrant collection name.
    Rules:
      - lowercase
      - only letters, digits, hyphen, underscore
    """
    name = model_name.lower()
    name = re.sub(r'[^a-z0-9\-_]+', '-', name)  # replace invalid chars
    name = re.sub(r'-+', '-', name).strip('-_')  # collapse multiple hyphens/underscores
    return name


def to_weaviate_class(model_name: str) -> str:
    """
    Converts a model name into a valid Weaviate class name.
    Rules:
      - starts with uppercase letter
      - letters and digits only (no symbols)
      - CamelCase-ish
    """
    # Replace non-alphanumeric with spaces, split, capitalize each part
    parts = re.split(r'[^A-Za-z0-9]+', model_name)
    parts = [p.capitalize() for p in parts if p]
    name = "".join(parts)
    # Ensure starts uppercase
    if not name:
        name = "Model"
    elif not name[0].isalpha():
        name = "M" + name
    return name
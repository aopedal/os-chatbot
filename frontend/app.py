import streamlit as st
import httpx
import json
import re
import utils.config as app_config

import uuid

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

st.set_page_config(page_title="HårekBot", page_icon="💬", layout="centered")
st.title("💬 Spør HårekBot")

# ------------------------------
# Fetch backend config
# ------------------------------
@st.cache_data
def get_config():
    res = httpx.get(f"{app_config.RETRIEVAL_URL}/config", timeout=10)
    res.raise_for_status()
    return res.json()

config = get_config()

# ------------------------------
# Sidebar configuration
# ------------------------------
st.sidebar.header("⚙️ Configuration")
inference_model = st.sidebar.selectbox(
    "Inference Model",
    options=[m["id"] for m in config["inference_model"]],
    format_func=lambda x: next(m["name"] for m in config["inference_model"] if m["id"] == x),
)
embedding_model = st.sidebar.selectbox(
    "Embedding Model",
    options=[m["id"] for m in config["embedding_model"]],
    format_func=lambda x: next(m["name"] for m in config["embedding_model"] if m["id"] == x),
)
vector_db = st.sidebar.selectbox(
    "Vector Database",
    options=[m["id"] for m in config["vector_db"]],
    format_func=lambda x: next(m["name"] for m in config["vector_db"] if m["id"] == x),
)

# ------------------------------
# Chat messages in session
# ------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------------------
# Helper: Convert {ref:ID} → Markdown links
# ------------------------------
def replace_placeholders(text, sources):
    return re.sub(
        r"\{ref:(.*?)\}",
        lambda m: f"[{m.group(1)}]({sources[m.group(1)]})" if m.group(1) in sources else m.group(1),
        text,
    )

# ------------------------------
# Helper: Fix LaTeX for Streamlit/KaTeX
# ------------------------------
def fix_latex_for_streamlit(text: str) -> str:
    # Block math: \[ ... \] -> $$ ... $$
    def repl(m):
        indent = m.group("indent") or ""
        content = m.group("content").strip()
        # Two newlines after $$ to separate following markdown
        return f"\n{indent}$$\n{indent}{content}\n{indent}$$\n\n"

    text = re.sub(
        r"(?:\n(?P<indent>[ \t]*))*\\\[(?P<content>.*?)\\\](?:\n[ \t]*)*",
        repl,
        text,
        flags=re.S
    )
    # Inline math: \( ... \) -> $ ... $
    text = re.sub(
        r"\\\(\s*(.*?)\s*\\\)",
        lambda m: f"${m.group(1).strip()}$",
        text,
        flags=re.S,
    )
    return text

# Escape KaTeX special characters inside \text{}
def fix_katex_special_chars(text: str) -> str:
    def repl(m):
        content = m.group(1)
        content = content.replace("#", r"\#")
        return f"\\text{{{content}}}"
    return re.sub(r"\\text\{(.*?)\}", repl, text, flags=re.S)

# Full postprocessing pipeline
def postprocess_text(text: str, sources: dict) -> str:
    text = fix_latex_for_streamlit(text)
    text = fix_katex_special_chars(text)
    text = replace_placeholders(text, sources)
    return text

# ------------------------------
# Display chat history
# ------------------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"])

# ------------------------------
# Chat input
# ------------------------------
if prompt := st.chat_input("Skriv en melding …"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    placeholder = st.chat_message("assistant").container()
    message_area = placeholder.empty()

    raw_buffer = ""
    sources = {}

    try:
        with httpx.stream(
            "POST",
            f"{app_config.RETRIEVAL_URL}/chat/stream",
            json={
                "user_id": st.session_state.user_id,
                "message": prompt,
                "inference_model": inference_model,
                "embedding_model": embedding_model,
                "vector_db": vector_db,
            },
            timeout=None,
        ) as response:
            for line in response.iter_lines():
                if not line:
                    continue

                chunk = json.loads(line)

                if chunk["type"] == "sources":
                    for src in chunk["sources"]:
                        sources[src["identifier"]] = src["url"]

                elif chunk["type"] == "delta":
                    raw_buffer += chunk["text"]
                    # Stream partial message safely
                    message_area.markdown(postprocess_text(raw_buffer, sources))

                elif chunk["type"] == "done":
                    break

    except Exception as e:
        raw_buffer += f"\n\n---\nFeil ved kommunikasjon med backend: {e}"

    # Final render & store
    final_message = postprocess_text(raw_buffer, sources)
    message_area.markdown(final_message)
    print(final_message)

    st.session_state.messages.append({
        "role": "assistant",
        "content": final_message
    })

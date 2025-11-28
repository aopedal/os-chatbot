import streamlit as st
import httpx
import json
import re
import utils.config as app_config

st.set_page_config(page_title="HårekBot", page_icon="💬", layout="centered")
st.title("💬 Spør HårekBot")

# Fetch backend config
@st.cache_data
def get_config():
    res = httpx.get(f"{app_config.RETRIEVAL_URL}/config", timeout=10)
    res.raise_for_status()
    return res.json()

config = get_config()

# Sidebar configuration
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

# Chat messages in session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"], unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Skriv en melding …"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    placeholder = st.chat_message("assistant").container()
    message_area = placeholder.empty()

    raw_buffer = ""
    sources = {}

    def replace_placeholders(text):
        return re.sub(
            r"\{([^\{\}]+)\}",
            lambda m: f"<a href='{sources.get(m.group(1), '#')}' target='_blank'>[{m.group(1)}]</a>",
            text
        )

    try:
        with httpx.stream(
            "POST",
            f"{app_config.RETRIEVAL_URL}/chat/stream",
            json={
                "message": prompt,
                "inference_model": inference_model,
                "embedding_model": embedding_model,
                "vector_db": vector_db,
            },
            timeout=None
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
                    message_area.markdown(replace_placeholders(raw_buffer), unsafe_allow_html=True)

                elif chunk["type"] == "done":
                    break

    except Exception as e:
        raw_buffer += f"\n\n---\nFeil ved kommunikasjon med backend: {e}"

    final_message = replace_placeholders(raw_buffer)
    message_area.markdown(final_message, unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": final_message
    })

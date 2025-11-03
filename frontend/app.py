import streamlit as st
import requests
import re

st.set_page_config(page_title="HårekBot", page_icon="💬", layout="centered")
st.title("💬 Spør HårekBot")

# --- Fetch available backend options ---
@st.cache_data
def get_config():
    res = requests.get("http://localhost:8080/config", timeout=10)
    res.raise_for_status()
    return res.json()

config = get_config()

# --- Dropdowns ---
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

# --- Chat Interface ---

# Store chat messages in Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"], unsafe_allow_html=True)

# User input
if prompt := st.chat_input("Skriv en melding …"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Initialize variables with default string values
    answer = "❌ Ingen respons fra serveren."
    data = {}
    
    try:
        res = requests.post(
            "http://localhost:8080/chat",
            json={
                "message": prompt,
                "inference_model": inference_model,
                "embedding_model": embedding_model,
                "vector_db": vector_db,
            },
            timeout=60
        )
        res.raise_for_status()
        
        data = res.json()
        # Set answer, relying on the server response's 'answer' field
        answer = data.get("answer") 
        if answer is None:
            answer = "❌ Serveren returnerte et uventet tomt svar."
            
    except Exception as e:
        answer = f"❌ Feil ved kommunikasjon med backend: {e}"

    # Replace occurrences of source text in the answer with clickable links
    display_content = answer
    sources = data.get("sources", [])
    for src in sources:
        # Match ID in square brackets, e.g. [linux9.2]
        pattern = re.escape(f"[{src['identifier']}]")
        link = f"<a href='{src['url']}' target='_blank'>[{src['identifier']}]</a>"
        display_content = re.sub(pattern, link, display_content)

    # Store and display
    st.session_state.messages.append({
        "role": "assistant",
        "content": display_content,
        "raw_answer": answer,
        "sources": sources
    })
    st.chat_message("assistant").markdown(display_content, unsafe_allow_html=True)
import httpx
import streamlit as st

import utils.config as app_config
from chat import render_chat
from sidebar import render_sidebar
from state import init_state

st.set_page_config(page_title=app_config.CHATBOT_NAME, page_icon="💬", layout="centered")
st.title(f"💬 Spør {app_config.CHATBOT_NAME}")

init_state()


@st.cache_data
def fetch_backend_config():
    res = httpx.get(f"{app_config.SERVER_URL}/config", timeout=10)
    res.raise_for_status()
    return res.json()


backend_config = fetch_backend_config()

# Hard-coded for now; could be moved to the sidebar when model selection is needed
inference_model = "gpt-oss-20b"
embedding_model = "Alibaba-NLP/gte-multilingual-base"
vector_db = "weaviate"

# Available collections; in future these should come from backend_config
available_collections = [
    {"id": "course_page", "name": "Kurssider"},
    {"id": "video_transcript", "name": "Videotranskripsjoner"},
]

render_sidebar(available_collections)
render_chat(inference_model, embedding_model, vector_db)

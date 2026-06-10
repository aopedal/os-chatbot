import httpx
import streamlit as st
from chat import render_chat
from sidebar import render_sidebar
from state import init_state

import utils.config as app_config


@st.fragment(run_every=10)
def _poll_config_mtime():
    if not st.session_state.debug_mode:
        return
    try:
        res = httpx.get(
            f"{app_config.SERVER_URL}/config/mtime", timeout=5
        )
        res.raise_for_status()
        new_mtime = res.json().get("loaded_at")
    except Exception:
        return
    last_mtime = st.session_state.last_config_mtime
    if last_mtime is None:
        st.session_state.last_config_mtime = new_mtime
        return
    if new_mtime and new_mtime != last_mtime:
        st.session_state.messages.append({
            "role": "notice",
            "content": f"settings.toml er oppdatert · {new_mtime}",
        })
        st.session_state.last_config_mtime = new_mtime
        st.rerun()

st.set_page_config(
    page_title=app_config.CHATBOT_NAME, page_icon="💬", layout="centered"
)
st.title(f"💬 Spør {app_config.CHATBOT_NAME}")

init_state()
_poll_config_mtime()


@st.cache_data
def fetch_backend_config():
    res = httpx.get(f"{app_config.SERVER_URL}/config", timeout=10)
    res.raise_for_status()
    return res.json()


try:
    backend_config = fetch_backend_config()
except (httpx.ConnectError, httpx.TimeoutException):
    st.info(
        "Venter på at backend-serveren skal bli klar. Siden lastes automatisk på nytt …"
    )
    st.stop()
except Exception as e:
    st.error(f"Klarte ikke å koble til backend: {e}")
    st.stop()

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

import json
import re

import httpx
import streamlit as st
from debug import render_debug_panel

import utils.config as app_config

# ---- Text postprocessing ----


def _fix_latex(text: str) -> str:
    def repl(m):
        indent = m.group("indent") or ""
        content = m.group("content").strip()
        return f"\n{indent}$$\n{indent}{content}\n{indent}$$\n\n"

    text = re.sub(
        r"(?:\n(?P<indent>[ \t]*))*\\\[(?P<content>.*?)\\\](?:\n[ \t]*)*",
        repl,
        text,
        flags=re.S,
    )
    text = re.sub(
        r"\\\(\s*(.*?)\s*\\\)",
        lambda m: f"${m.group(1).strip()}$",
        text,
        flags=re.S,
    )
    return text


def _fix_katex_special_chars(text: str) -> str:
    def repl(m):
        content = m.group(1).replace("#", r"\#")
        return f"\\text{{{content}}}"

    return re.sub(r"\\text\{(.*?)\}", repl, text, flags=re.S)


def _replace_placeholders(text: str, sources: dict) -> str:
    return re.sub(
        r"\{ref:(.*?)\}",
        lambda m: (
            f"[{m.group(1)}]({sources[m.group(1)]})"
            if m.group(1) in sources
            else m.group(1)
        ),
        text,
    )


def postprocess_text(text: str, sources: dict) -> str:
    text = _fix_latex(text)
    text = _fix_katex_special_chars(text)
    text = _replace_placeholders(text, sources)
    return text


# ---- Chat UI ----


def render_chat(inference_model: str, embedding_model: str, vector_db: str):
    for msg in st.session_state.messages:
        if msg["role"] == "notice":
            st.markdown(
                "<div style='"
                "text-align:center;"
                "color:gray;"
                "font-size:0.8em;"
                "padding:0.4em 0"
                f"'>─── {msg['content']} ───</div>",
                unsafe_allow_html=True,
            )
        elif msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").markdown(msg["content"])
            if st.session_state.debug_mode and msg.get("debug_data"):
                render_debug_panel(msg["debug_data"])

    with st.bottom:
        st.caption(
            f"{app_config.CHATBOT_NAME} er en språkmodell og kan gjøre feil. "
            "Dobbeltsjekk svarene du får."
        )

    if prompt := st.chat_input("Skriv en melding …"):
        _handle_input(prompt, inference_model, embedding_model, vector_db)


def _handle_input(
    prompt: str, inference_model: str, embedding_model: str, vector_db: str
):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    message_area = st.chat_message("assistant").container().empty()
    debug_placeholder = st.empty()
    raw_buffer = ""
    sources: dict[str, str] = {}
    debug_data: dict = {
        "request": None,
        "sources": [],
        "server_debug": [],
        "config_mtime": None,
    }

    request_payload = {
        "user_id": st.session_state.user_id,
        "message": prompt,
        "inference_model": inference_model,
        "embedding_model": embedding_model,
        "vector_db": vector_db,
        "socratic_mode": st.session_state.socratic_mode,
        "active_collections": st.session_state.active_collections,
    }
    debug_data["request"] = request_payload

    try:
        with httpx.stream(
            "POST",
            f"{app_config.SERVER_URL}/chat/stream",
            json=request_payload,
            timeout=None,
        ) as response:
            for line in response.iter_lines():
                if not line:
                    continue
                chunk = json.loads(line)

                if chunk["type"] == "sources":
                    for src in chunk["sources"]:
                        sources[src["identifier"]] = src["url"]
                    debug_data["sources"] = chunk["sources"]

                elif chunk["type"] == "delta":
                    raw_buffer += chunk["text"]
                    message_area.markdown(postprocess_text(raw_buffer, sources))

                elif chunk["type"] == "debug":
                    if chunk.get("step") == "config":
                        debug_data["config_mtime"] = chunk["data"].get("loaded_at")
                    debug_data["server_debug"].append(chunk)
                    if st.session_state.debug_mode:
                        with debug_placeholder.container():
                            render_debug_panel(debug_data)

                elif chunk["type"] == "done":
                    break

    except Exception as e:
        raw_buffer += f"\n\n---\nFeil ved kommunikasjon med backend: {e}"

    final_message = postprocess_text(raw_buffer, sources)
    message_area.markdown(final_message)

    new_mtime = debug_data.get("config_mtime")
    last_mtime = st.session_state.last_config_mtime

    if st.session_state.debug_mode:
        with debug_placeholder.container():
            render_debug_panel(debug_data)
        if new_mtime and last_mtime is not None and new_mtime != last_mtime:
            st.session_state.messages.append({
                "role": "notice",
                "content": f"settings.toml er oppdatert · {new_mtime}",
            })

    if new_mtime:
        st.session_state.last_config_mtime = new_mtime

    st.session_state.messages.append({
        "role": "assistant",
        "content": final_message,
        "debug_data": debug_data,
    })

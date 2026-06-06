import streamlit as st


def render_debug_panel(debug_data: dict):
    with st.expander("Debug", expanded=True):
        if request := debug_data.get("request"):
            st.subheader("Request")
            st.json(request)

        steps = debug_data.get("server_debug", [])
        if steps:
            for step in steps:
                _render_step(step)
        else:
            st.caption(
                "Server-side debug steps will appear here when debug mode is active. "
                "Add new steps by yielding `{\"type\": \"debug\", \"step\": \"<name>\", \"data\": ...}` "
                "events in `server.py`'s `event_stream()` before the `done` event."
            )


def _render_step(step: dict):
    name = step.get("step", "unknown")
    data = step.get("data")

    if name == "retrieval":
        st.subheader("Context sources")
        _render_retrieval(data or [])

    elif name == "memory":
        st.subheader("Conversation memory")
        _render_memory(data or [])

    else:
        st.subheader(f"Debug: {name}")
        st.json(data)


def _render_retrieval(payloads: list[dict]):
    if not payloads:
        st.caption("No chunks retrieved.")
        return

    by_type: dict[str, list] = {}
    for p in payloads:
        by_type.setdefault(p.get("type", "unknown"), []).append(p)

    for type_id, chunks in by_type.items():
        st.markdown(f"**{type_id}** — {len(chunks)} chunk(s)")
        for chunk in chunks:
            identifier = chunk.get("identifier") or chunk.get("chunk_id") or "—"
            with st.expander(identifier):
                if url := chunk.get("url"):
                    st.markdown(f"**URL:** {url}")
                st.text(chunk.get("text", ""))


def _render_memory(messages: list[dict]):
    if not messages:
        st.caption("No conversation memory.")
        return

    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        preview = content[:60] + ("…" if len(content) > 60 else "")
        with st.expander(f"{role.capitalize()}: {preview}"):
            st.text(content)

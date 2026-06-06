import uuid
import streamlit as st


def render_sidebar(available_collections: list[dict]):
    with st.sidebar:
        st.header("Innstillinger")

        st.toggle(
            "Pedagogisk modus", key="socratic_mode",
            help="Gir hint og veiledning i stedet for direkte svar.",
        )
        st.toggle(
            "Debug-modus", key="debug_mode",
            help="Vis forespørsel, hentede kilder og andre mellomtrinn. Kan også aktiveres via ?debug=1 i URL-en.",
        )

        st.divider()
        _render_collection_toggles(available_collections)

        st.divider()
        _render_conversation_history()


def _render_collection_toggles(available_collections: list[dict]):
    st.subheader("Kunnskapskilder")
    if not available_collections:
        st.caption("Ingen samlinger tilgjengelig.")
        return

    active = []
    for col in available_collections:
        # value=True is only used on first render; widget state persists via key after that
        if st.checkbox(col["name"], value=True, key=f"col_{col['id']}"):
            active.append(col["id"])

    all_ids = {c["id"] for c in available_collections}
    st.session_state.active_collections = None if set(active) == all_ids else active


def _render_conversation_history():
    st.subheader("Tidligere samtaler")

    if st.button("Ny samtale", use_container_width=True):
        _save_and_clear()
        st.rerun()

    conversations = st.session_state.conversations
    if not conversations:
        st.caption("Ingen samtaler lagret i denne økten.")
        return

    for conv in reversed(conversations):
        if st.button(conv["title"], key=f"conv_{conv['id']}", use_container_width=True):
            _save_and_clear()
            st.session_state.messages = list(conv["messages"])
            st.session_state.user_id = conv["user_id"]
            st.rerun()


def _save_and_clear():
    if st.session_state.messages:
        first_user_msg = next(
            (m["content"] for m in st.session_state.messages if m["role"] == "user"),
            "Samtale",
        )
        title = first_user_msg[:40] + ("…" if len(first_user_msg) > 40 else "")
        st.session_state.conversations.append({
            "id": str(uuid.uuid4()),
            "title": title,
            "messages": list(st.session_state.messages),
            "user_id": st.session_state.user_id,
        })
    st.session_state.messages = []
    st.session_state.user_id = str(uuid.uuid4())

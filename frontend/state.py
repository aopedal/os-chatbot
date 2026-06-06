import uuid
import streamlit as st


def init_state():
    defaults = {
        "user_id": str(uuid.uuid4()),
        "messages": [],
        "conversations": [],    # list of {id, title, messages, user_id}
        "socratic_mode": False,
        "active_collections": None,  # None means all enabled
        "debug_mode": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Allow activating debug mode via URL: ?debug=1
    if "debug" in st.query_params:
        st.session_state.debug_mode = True

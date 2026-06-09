import uuid

import streamlit as st


def init_state():
    defaults = {
        "user_id": str(uuid.uuid4()),
        "messages": [],
        "conversations": [],  # list of {id, title, messages, user_id}
        "socratic_mode": "off",
        "active_collections": None,  # None means all enabled
        "debug_mode": False,
        "last_config_mtime": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Restore preferences from URL params on first load only.
    # Guarded by a sentinel so subsequent rerenders don't override user changes.
    # _sync_prefs_to_url() in sidebar.py keeps the URL in sync after the first load.
    if "prefs_loaded_from_url" not in st.session_state:
        if "debug" in st.query_params:
            st.session_state.debug_mode = True
        if "socratic" in st.query_params:
            raw = st.query_params["socratic"]
            if raw in ("auto", "always"):
                st.session_state.socratic_mode = raw
        if "collections" in st.query_params:
            raw = st.query_params["collections"]
            st.session_state.active_collections = raw.split(",") if raw else None
        st.session_state.prefs_loaded_from_url = True

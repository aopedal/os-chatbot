import streamlit as st
import requests

st.set_page_config(page_title="My LLM Chat", page_icon="💬", layout="centered")

st.title("💬 Chat with My LLM")

# Store chat messages in Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

# User input
if prompt := st.chat_input("Skriv en melding …"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Send request to your backend
    try:
        res = requests.post(
            "http://localhost:8080/chat",
            json={"message": prompt},
            timeout=60
        )
        res.raise_for_status()
        data = res.json()
        answer = data.get("answer", "❌ Feil: ingen respons fra serveren.")
    except Exception as e:
        answer = f"❌ Feil ved tilkobling til serveren: {e}"

    # Display assistant message
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)

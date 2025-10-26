import streamlit as st
import requests

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
    options=[m["id"] for m in config["inference_models"]],
    format_func=lambda x: next(m["name"] for m in config["inference_models"] if m["id"] == x),
)
embedding_model = st.sidebar.selectbox(
    "Embedding Model",
    options=[m["id"] for m in config["embedding_models"]],
    format_func=lambda x: next(m["name"] for m in config["embedding_models"] if m["id"] == x),
)
vector_db = st.sidebar.selectbox(
    "Vector Database",
    options=[m["id"] for m in config["vector_dbs"]],
    format_func=lambda x: next(m["name"] for m in config["vector_dbs"] if m["id"] == x),
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
        st.chat_message("assistant").write(msg["content"])

# User input
if prompt := st.chat_input("Skriv en melding …"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Initialize variables with default string values
    answer = "❌ Ingen respons fra serveren."
    unique_sources = []
    
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

        # Extract sources
        sources = data.get("sources", [])
        unique_sources = list(set(sources)) 
            
    except Exception as e:
        answer = f"❌ Feil ved kommunikasjon med backend: {e}"
        unique_sources = [] # Clear sources on communication error

    # Prepare the message content for display and history
    display_content = answer # display_content is now guaranteed to be a string

    if unique_sources:
        # Create clickable links... (rest of your source logic)
        source_links = [
            f"- <a href='http://localhost:8080/docs/{src}' target='_blank'>{src}</a>"
            for src in unique_sources
        ]
        
        # Add the sources to the display content
        sources_md = "\n\n**Kilder:**\n" + "\n".join(source_links)
        display_content += sources_md # This is now safe as display_content is a string

    # Store the full content in the session state... (rest of the code)
    st.session_state.messages.append({"role": "assistant", "content": display_content, "raw_answer": answer, "sources": unique_sources})

    # Display the full content
    st.chat_message("assistant").markdown(display_content, unsafe_allow_html=True)
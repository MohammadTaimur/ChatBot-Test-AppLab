import streamlit as st
import requests

# 🔧 Change this to your FastAPI base URL
API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="📄 PDF Chatbot", layout="centered")
st.title("📄🧠 Chat with your PDF")

# Keep chat history in Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Upload PDF ---
st.subheader("Upload a PDF")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    if st.button("Upload PDF"):
        files = {"file": uploaded_file}
        with st.spinner("Processing PDF..."):
            resp = requests.post(f"{API_BASE}/Upload-PDF", files=files)
        if resp.status_code == 200:
            st.success("✅ PDF uploaded and indexed successfully!")
            st.session_state.messages = []  # reset chat when new file is uploaded
        else:
            st.error(f"❌ Error: {resp.json()['detail']}")

# --- Chat Section ---
st.subheader("Chat with your PDF")

if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""

query = st.text_input("Ask a question:", value=st.session_state.chat_input)

if st.button("Send") and query.strip():
    with st.spinner("Thinking..."):
        data = {"query": query}
        resp = requests.post(f"{API_BASE}/Chatbot", data=data)

    if resp.status_code == 200:
        answer = resp.text
        # Save chat
        st.session_state.messages.append({"role": "user", "content": query})
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.chat_input = ""  # clear input
    else:
        st.error(f"❌ Error: {resp.json()['detail']}")

# --- Display Chat History ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**👤 You:** {msg['content']}")
    else:
        # Render assistant messages as Markdown
        st.markdown(f"**🤖 Assistant:**\n\n{msg['content']}", unsafe_allow_html=True)
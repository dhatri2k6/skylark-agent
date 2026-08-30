import streamlit as st
from agent import chat

st.set_page_config(page_title="Skylark BI Agent")
st.title("Skylark Drones — BI Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "display_messages" not in st.session_state:
    st.session_state.display_messages = []

for role, text in st.session_state.display_messages:
    with st.chat_message(role):
        st.markdown(text)

user_input = st.chat_input("Ask a business question...")
if user_input:
    st.session_state.display_messages.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("Thinking..."):
        reply, st.session_state.messages = chat(st.session_state.messages)

    st.session_state.display_messages.append(("assistant", reply))
    with st.chat_message("assistant"):
        st.markdown(reply)
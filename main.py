import streamlit as st
from agent import process_message_and_replace_token

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"], unsafe_allow_html=True)

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.write(prompt, unsafe_allow_html=True)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Process user input using agent.py function
    assistant_response = process_message_and_replace_token(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.write(assistant_response, unsafe_allow_html=True)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

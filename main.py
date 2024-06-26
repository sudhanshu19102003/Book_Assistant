import streamlit as st
from agent import BookAssistant
import glob, os

# Section: Initialize BookAssistant instance
def get_assistant():
    #find all json files in the current directory and delete the
    if "assistant" not in st.session_state:
        st.session_state.assistant = BookAssistant()
    return st.session_state.assistant

# Section: Initialize Session State
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def main():
    # Initialize session state
    initialize_session_state()
    assistant = get_assistant()
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
        assistant_response = assistant.run(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.write(assistant_response, unsafe_allow_html=True)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

if __name__ == "__main__":
    main()
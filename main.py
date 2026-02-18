import streamlit as st
from agent import BookAssistant
import streamlit.components.v1 as components

# Configure Streamlit page
st.set_page_config(layout="wide")


# Section: Initialize BookAssistant instance
def get_assistant():
    # find all json files in the current directory and delete the
    if "assistant" not in st.session_state:
        st.session_state.assistant = BookAssistant()
    return st.session_state.assistant


# Section: Initialize Session State
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []


def render_message(content):
    """Render message content, handling HTML tables specially"""
    if '<div class="books-layout">' in content:
        # Process multiple tables by finding all table blocks
        remaining_content = content

        while "<style>" in remaining_content:
            # Find the start of the table block
            table_start = remaining_content.find("<style>")

            # Render any text/markdown before this table
            text_before = remaining_content[:table_start].strip()
            if text_before:
                st.markdown(text_before, unsafe_allow_html=True)

            # Find the end of this table block (</script> tag)
            table_end = remaining_content.find("</script>", table_start) + len(
                "</script>"
            )

            # Extract and render this table
            table_html = remaining_content[table_start:table_end]

            # Calculate dynamic height based on number of rows
            # Count the number of table rows in this table
            row_count = table_html.count('<tr class="book-row"')
            # Base height (header + padding) + row height * number of rows
            # Each row is approximately 110px (90px cover + 20px padding)
            # Add 100px for header and container padding
            calculated_height = min(100 + (row_count * 115), 850)

            components.html(table_html, height=calculated_height, scrolling=False)

            # Move to the remaining content after this table
            remaining_content = remaining_content[table_end:]

        # Render any remaining text after all tables
        if remaining_content.strip():
            st.markdown(remaining_content.strip(), unsafe_allow_html=True)
    else:
        # Regular text message - use markdown for proper rendering
        st.markdown(content, unsafe_allow_html=True)


def create_status_callback(status_container):
    """Create a status callback function for tool execution updates.

    Args:
        status_container: Streamlit status container to write updates to

    Returns:
        Callback function that accepts (tool_name: str, status: str)
    """

    def update_status(tool_name: str, status: str):
        """Update the status display when tools are called"""
        tool_messages = {
            "googleAPI_retrieval": {
                "start": "🔍 **Searching Google Books API** - Fetching book data from external source...",
                "complete": "✅ **Books Retrieved** - Successfully downloaded book information",
            },
            "present_book_info": {
                "start": "📊 **Preparing Results** - Formatting book information for display...",
                "complete": "✅ **Table Ready** - Book information formatted and ready to view",
            },
            "search_db": {
                "start": "🔎 **Searching Database** - Looking through stored book information...",
                "complete": "✅ **Search Complete** - Found matching books in database",
            },
            "get_book_by_rank": {
                "start": "📖 **Fetching Book Details** - Retrieving specific book information...",
                "complete": "✅ **Details Retrieved** - Book information loaded successfully",
            },
        }

        message = tool_messages.get(tool_name, {}).get(
            status, f"⚙️ {tool_name}: {status}"
        )
        status_container.write(message)

    return update_status


def display_chat_history():
    """Display all messages from chat history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            render_message(message["content"])


def handle_user_input(prompt: str, assistant: BookAssistant):
    """Handle user input and generate assistant response.

    Args:
        prompt: User's input message
        assistant: BookAssistant instance
    """
    # Display user message in chat message container
    with st.chat_message("user"):
        st.write(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Create a status container for tool execution updates
    with st.chat_message("assistant"):
        status_container = st.status("Processing your request...", expanded=True)

        # Create status callback
        status_callback = create_status_callback(status_container)

        # Process user input using agent.py function with status callback
        assistant_response = assistant.run(prompt, status_callback=status_callback)

        # Update status to complete
        status_container.update(
            label="✅ Request completed", state="complete", expanded=False
        )

        # Display assistant response
        render_message(assistant_response)

    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_response}
    )


def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()
    assistant = get_assistant()

    # Display chat messages from history on app rerun
    display_chat_history()

    # React to user input
    if prompt := st.chat_input("What is up?"):
        handle_user_input(prompt, assistant)


if __name__ == "__main__":
    main()

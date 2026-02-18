"""Book Assistant agent with LangGraph orchestration."""

import json
import uuid

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition
from datetime import datetime

from agent_tools import (
    googleAPI_retrieval,
    present_book_info,
    search_db,
    get_book_by_rank,
)
from components.book_table_renderer import BookTableRenderer
from tools import Assistant, State, create_tool_node_with_fallback
from utils.file_manager import FileManager

TOKEN_START = "<data_retrieved="
TOKEN_END = ">"


class BookAssistant:
    """Agent for retrieving and presenting book information."""

    def __init__(self) -> None:
        self.llm = ChatAnthropic(model="claude-haiku-4-5-20251001", temperature=0)
        self.primary_assistant_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant to retrieve book information. "
                    "Use the provided tools to download book information based on user's search criteria "
                    "(keywords, category, title, author, or ISBN) and then present the information using tokens. "
                    "You can combine multiple keywords or categories in a single search query "
                    "(e.g., 'science fiction adventure' or 'mystery thriller'). "
                    "When using tools, be persistent. "
                    "\nWorkflow:"
                    "1. Call googleAPI_retrieval - this returns a unique search_id"
                    "2. Extract the search_id from the response (it will be in format 'Search ID: <uuid>')"
                    "3. Call present_book_info with that search_id to display the results"
                    "4. You can display results from MULTIPLE searches by calling present_book_info "
                    "multiple times with different search_ids"
                    "\nImportant Notes:"
                    "1. Independent recommendations of books is strictly prohibited."
                    "2. The database has no information initially."
                    "3. Maintain the exact format provided by the tool for tokens and place all tokens in the final response."
                    "4. Tokens are already rendered when the user sees the final response, so adjust your responses accordingly."
                    "5. Each googleAPI_retrieval call returns a unique search_id - save this to display those specific results."
                    "6. You can show books from multiple different searches in a single response.",
                ),
                ("placeholder", "{messages}"),
            ]
        ).partial(time=datetime.now())

        self.part_1_tools = [
            googleAPI_retrieval,
            present_book_info,
            search_db,
            get_book_by_rank,
        ]

        self.part_1_assistant_runnable = (
            self.primary_assistant_prompt | self.llm.bind_tools(self.part_1_tools)
        )

        builder = StateGraph(State)
        builder.add_node("assistant", Assistant(self.part_1_assistant_runnable))
        builder.add_node("tools", create_tool_node_with_fallback(self.part_1_tools))
        builder.set_entry_point("assistant")
        builder.add_conditional_edges("assistant", tools_condition)
        builder.add_edge("tools", "assistant")

        try:
            memory = SqliteSaver.from_conn_string(":memory:")
        except Exception:
            raise Exception("Could not create memory database")

        self.part_1_graph = builder.compile(checkpointer=memory)
        self.thread_id = str(uuid.uuid4())
        self._renderer = BookTableRenderer()
        self._file_manager = FileManager()

    def replace_token_with_table(self, text: str) -> str:
        """Replace <data_retrieved=TOKEN> placeholders with rendered HTML tables."""
        tables_html: list[str] = []

        while True:
            start_idx = text.find(TOKEN_START)
            end_idx = text.find(TOKEN_END, start_idx)

            if start_idx == -1 or end_idx == -1:
                break

            token_value = text[start_idx + len(TOKEN_START) : end_idx]
            json_filename = f"{token_value}.json"

            try:
                data = self._file_manager.read_books_json(json_filename)
                unique_id = token_value.replace("-", "_")

                html_table = self._renderer.render_from_dicts(
                    books_data=data,
                    unique_id=unique_id,
                    include_styles=True,
                )
                tables_html.append(html_table)

                text = (
                    text[:start_idx]
                    + f"__TABLE_PLACEHOLDER_{len(tables_html) - 1}__"
                    + text[end_idx + len(TOKEN_END) :]
                )

            except FileNotFoundError:
                text = (
                    text[:start_idx]
                    + f"[Error: Token {token_value} not found]"
                    + text[end_idx + len(TOKEN_END) :]
                )
            except (json.JSONDecodeError, ValueError):
                text = (
                    text[:start_idx]
                    + f"[Error: Invalid data for token {token_value}]"
                    + text[end_idx + len(TOKEN_END) :]
                )

        for i, table_html in enumerate(tables_html):
            text = text.replace(f"__TABLE_PLACEHOLDER_{i}__", table_html)

        return text

    def run(self, question: str, status_callback=None) -> str:
        """Process user question and return response with rendered tables.

        Args:
            question: User's question
            status_callback: Optional callback function to report status updates.
                           Should accept (tool_name: str, status: str) where status is 'start' or 'complete'
        """
        events = self.part_1_graph.stream(
            {"messages": ("user", question)},
            {"configurable": {"thread_id": self.thread_id}},
            stream_mode="values",
        )
        last_event = None
        for event in events:
            last_event = event

            # Check if we have tool calls in the last message
            if event.get("messages"):
                last_message = event["messages"][-1]

                # If the message has tool_calls, it means tools are about to be executed
                if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                    for tool_call in last_message.tool_calls:
                        tool_name = tool_call.get("name", "Unknown tool")
                        if status_callback:
                            status_callback(tool_name, "start")

                # If the message is a ToolMessage, it means a tool has completed
                if hasattr(last_message, "type") and last_message.type == "tool":
                    if hasattr(last_message, "name"):
                        tool_name = last_message.name
                        if status_callback:
                            status_callback(tool_name, "complete")

        content = last_event["messages"][-1].content if last_event else "No response."
        return self.replace_token_with_table(content)


if __name__ == "__main__":
    assistant = BookAssistant()
    print(
        assistant.run("find 5 books about science?")
        + " "
        + assistant.run("repeat your last response?")
    )

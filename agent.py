from agent_tools import googleAPI_retrieval, present_book_info, search_db
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from tools import create_tool_node_with_fallback, Assistant, State
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import tools_condition
import uuid
import json

class BookAssistant:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0)
        self.primary_assistant_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant to retrieve book information. "
                    "Use the provided tools to first download book information of a given category and then present the information of books using the token. "
                    "When using tools, be persistent. "
                    "Note:"
                    "1. Independent recommendations of books is strictly prohibited."
                    "2. The database has no information initially."
                    "3. Maintain the exact format provided by the tool for the token generated. and place the token in the final response."
                    "4. the token is alredy rendered when the user sees the final response. so ajdust the responces as if the data is already there."
                ),
                ("placeholder", "{messages}"),
            ]
        ).partial(time=datetime.now())

        self.part_1_tools = [googleAPI_retrieval, present_book_info, search_db]

        self.part_1_assistant_runnable = self.primary_assistant_prompt | self.llm.bind_tools(self.part_1_tools)

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

    def replace_token_with_table(self,text):
        # Extract token_value from the text
        start_token = '<data_retrieved='
        end_token = '>'
        start_idx = text.find(start_token)
        end_idx = text.find(end_token, start_idx)

        if start_idx == -1 or end_idx == -1:
            return text  # Return original text if token format is not found

        token_value = text[start_idx + len(start_token):end_idx]
        json_filename = f"{token_value}.json"  # Assuming token_value.json format

        try:
            # Read JSON data from file
            with open(json_filename, 'r') as file:
                data = json.load(file)

            # Generate HTML table
            html_table = """
<style>
        .table-container {
            width: 100%;
            height: 300px; /* Adjust the height as needed */
            overflow-y: auto;
            border: 1px solid #ffbd45;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ffbd45;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #ffbd45;
        }
    </style>"""
            html_table += """<div class="table-container"><table>\n"""
            html_table += '<tr><th>No.</th><th>Title</th><th>Authors</th><th>Publisher</th><th>Published Date</th></tr>\n'
            index = 0
            for item in data:
                index += 1
                title = item.get('title', 'N/A')
                authors = ', '.join(item.get('authors', []))
                publisher = item.get('publisher', 'N/A')
                published_date = item.get('publishedDate', 'N/A')

                html_table += f'<tr><td>{index}</td><td>{title}</td><td>{authors}</td><td>{publisher}</td><td>{published_date}</td></tr>\n'

            html_table += '</table></div>\n'

            # Replace token in the original text with HTML table
            updated_text = text[:start_idx] + html_table + text[end_idx + 1:]

            return updated_text

        except FileNotFoundError:
            return text  # Return original text if JSON file is not found
        except json.JSONDecodeError:
            return text  # Return original text if JSON decoding fails

    def run(self, question):
        events = self.part_1_graph.stream(
            {"messages": ("user", question)},
            {"configurable": {"thread_id": self.thread_id}},
            stream_mode="values"
        )
        last_event = None
        for event in events:
            last_event = event
        return self.replace_token_with_table(last_event['messages'][-1].content if last_event else "No response.")

if __name__ == "__main__":
    assistant = BookAssistant()
    print(assistant.run("find 5 books about science?") + " " +assistant.run("repeat your last response?"))
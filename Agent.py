from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, StateGraph
from langchain_mistralai.chat_models import ChatMistralAI
from dotenv import load_dotenv
import os
from Researcher_tools import Researcher_tools

load_dotenv()

class Agent:
    def __init__(self):
        self.llm = ChatMistralAI(api_key=os.getenv('MISTRALAI_API_KEY'), temperature=0)
        self.Researcher_tools = Researcher_tools()
        self.user_message = ""
        self.response_message = ""

    def create_agent(self,tools):
        """Create an agent."""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK, another assistant with different tools "
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any of the other assistants have the final answer or deliverable,"
                    " prefix your response with FINAL ANSWER so the team knows to stop."
                    " You have access to the following tools: {tool_discreption}.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        tools = tools.get_tool_discreption()
        prompt = prompt.partial(tool_names=tools.tool_discreption())
        return prompt | self.llm.bind_tools(tools)

    def handle_message(self, message):
        self.user_message = message
        self.tools.get_tool_discreption()
        


    def start(self):
        print("AI Agent is now running. Type 'exit' to stop.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Shutting down the AI Agent.")
                break
            response = self.handle_message(user_input)
            print(f"AI: {response}")

if __name__ == '__main__':
    agent = Agent()
    agent.start()

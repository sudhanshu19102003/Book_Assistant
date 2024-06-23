from BookInfo import BookInfo
import chromadb as db
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.tools import BaseTool
from langchain.agents import AgentExecutor, create_react_agent
from langchain_mistralai.chat_models import ChatMistralAI
from dotenv import load_dotenv
from langchain.memory import ConversationBufferWindowMemory
import os
from langchain import hub
import json
from langchain_core.output_parsers import JsonOutputParser


load_dotenv()

class get_books_data(BaseTool):
    name = "google_books_data"
    description = """Retrieves information from Google Books API based on category..."""

    def _run(self, genre: str) -> str:
        try:
            book_info = BookInfo()
            book_info.category = genre.strip().lower()
            book_info.get_top_books()
            chroma_client = db.Client()
            book_collection = chroma_client.get_or_create_collection(name="book_info")
            documents = []
            metadatas = []
            ids = []
            for book in book_info.processed_results:
                authors = ", ".join(book['authors'])
                categories = ", ".join(book['categories'])
                info = f"""
                This book is ranked {book["rank"]}.
                Title: {book['title']} 
                Authors: {authors}
                Publisher: {book["publisher"]}
                Published Date: {book["publishedDate"]}
                Description: {book["description"]}"""
                documents.append(info)
                metadata = {
                    'rank': book["rank"],
                    'title': book['title'],
                    'authors': authors,
                    'category': categories,
                }
                metadatas.append(metadata)
                ids.append(str(book['rank']))
            book_collection.add(documents=documents, ids=ids, metadatas=metadatas)
            with open("data.json", 'w') as f:
                json.dump(metadatas, f)
            return "Data fetched successfully in the database. For the next step, use db_query tool to query the data."
        except Exception as e:
            return f"An error occurred while fetching data: {e}"

class db_query_tool(BaseTool):
    name = "db_query"
    description = "The function takes in a characteristic of the book you want to search for and returns the information of books with this characteristic in the database. Example: 'funny'."

    def _run(self, query: str) -> str:
        try:
            chroma_client = db.Client()
            book_collection = chroma_client.get_or_create_collection(name="book_info")
            results = book_collection.query(query_texts=query, n_results=3)
            paragraphs = ""
            for paragraph in results['documents'][0]:
                paragraphs += (paragraph + "\n")
            
            phrases =JsonOutputParser().parse(paragraphs)
            return paragraphs
        except Exception as e:
            return f"An error occurred while querying the database: {e}"

class get_data_from_db(BaseTool):
    name = "retrieve_data_from_db"
    description = "Retrieve information of top n books from the database. Defaults to top 3 books if not specified."

    def _run(self, number_of_entries: str) -> str:
        try:
            number_of_entries = int(number_of_entries)  # Convert input to integer
        except ValueError:
            number_of_entries = 3  # Default to 3 if invalid input
        try:
            with open("data.json", 'r') as f:
                data = json.load(f)
            results = []
            for index, book in enumerate(data[:number_of_entries], start=1):
                result = (
                    f"This book is ranked {index}.\n"
                    f"Title: {book['title']}\n"
                    f"Authors: {book['authors']}\n"
                    f"Category: {book['category']}\n\n"
                )
                results.append(result)
            output_string = '\n'.join(results)
            return output_string
        except Exception as e:
            return f"An error occurred while retrieving data: {e}"

if __name__ == '__main__':
    #first test the tools
    get_data = get_books_data()
    print(get_data.run("Fiction"))
    query_data = db_query_tool()
    print(query_data.run("funny"))
    retrieve_data = get_data_from_db()
    print(retrieve_data.run("3"))
    instructions = """
    You are an assistant that helps users find information about books.
Assistant is a large language model.
Assistant is designed to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. 
As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
Assistant should only use the tools provided to fetch the data and present it in a readable format. Remember, you can say no if you don't get any data from tools.

Process:
1. Fetch data from the Google Books API and store it in the database.
2. Query the database to get the required information.
3. Present the information in a clear and readable format.

Output format:
- When an action is needed, clearly indicate the action.
- Separate the final answer from any actions.

Example:
Thought: Do I need to use a tool? Yes
Action: google_books_data
Action Input: Fiction

Observation: Data from Google Books API has been stored in the database.

Thought: Do I need to use a tool? Yes
Action: retrieve_data_from_db
Action Input: 10

Observation: Retrieved data from the database.

Final Answer: Here are the top 10 Fiction books...
    """
    get_books_info = get_books_data()
    get_books_info_tool = db_query_tool()
    present_data_tool = get_data_from_db()
    tools = [get_books_info, present_data_tool]
    llm = ChatMistralAI(api_key=os.getenv('MISTRALAI_API_KEY'), temperature=0)
    memory = ConversationBufferWindowMemory(
        memory_key='chat_history',
        k=3,
        return_messages=True
    )
    base_prompt = hub.pull("langchain-ai/react-agent-template")
    prompt = base_prompt.partial(instructions=instructions)
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )
    agent_executor = AgentExecutor(agent=agent, memory=memory, tools=tools, handle_parsing_errors=True)     
    
    try:
        result = agent_executor.invoke({"input": "give me top 10 friction books"})
        print(result)
    except Exception as e:
        print(f"An error occurred during agent execution: {e}")

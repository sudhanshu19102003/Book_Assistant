import re
import json
from Tool import googleAPI_retrieval, present_book_info
from langgraph.prebuilt import create_react_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage
import os


def process_message_and_replace_token(input_message):
    json_file = ""
    # Define tools and initialize model and agent_executor
    input_message += """note: 1. Independent recommendations are not permitted.
2. first you need to download the information of the books of the given category to the database.
3. Maintain the exact format provided by the tool."""
    tools = [googleAPI_retrieval, present_book_info]
    model = ChatMistralAI(model="mistral-large-latest", temperature=0)
    agent_executor = create_react_agent(model, tools)
    
    # Invoke agent with input message
    response = agent_executor.invoke({"messages": [HumanMessage(content=input_message)]}, debug=False)
    final_message = None
    
    # Extract final message from response
    for message in response["messages"]:
        if message.response_metadata.get('finish_reason') == "stop":
            final_message = message.content
    
    if not final_message:
        print("No final message found.")
        return "Sorry, I could not find what you're looking for."
    
    # Find token in the final_message <data_retrieved=token> and replace it with data in token.json
    pattern = r'data_retrieved=([a-zA-Z0-9\-_]+)'
    match = re.search(pattern, final_message)
    
    if match:
        # Extract the token value
        token = match.group(1)
        
        # Assuming the JSON file name is based on the token value
        json_file = f'{token}.json'
        
        try:
            # Read data from the JSON file
            with open(json_file, 'r') as file:
                data = json.load(file)
                
            # Generate HTML table from JSON data
            html_table = """
<style>
    .scrollable-table {
        max-height: 600px; /* Set the max height of the div */
        overflow-y: auto; /* Enable vertical scrolling */
        border: 1px solid #ccc;
        padding: 10px;
    }
</style>
<div class="scrollable-table">
<table>
<tr>
    <th>No.</th>
    <th>Title</th>
    <th>Authors</th>
    <th>Publisher</th>
    <th>Published Date</th>
</tr>
"""
            number = 0
            for item in data:
                number += 1
                html_table += f"""
<tr>
    <td>{number}</td>
    <td>{item["title"]}</td>
    <td>{', '.join(item["authors"])}</td>
    <td>{item["publisher"]}</td>
    <td>{item["publishedDate"]}</td>
</tr>
"""
            
            html_table += '</table></div>'
            final_message = final_message.replace(match.group(0), html_table)
            if os.path.exists(json_file):
                os.remove(json_file)
            
        except FileNotFoundError:
            print(f"JSON file '{json_file}' not found.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON file '{json_file}': {e}")
    return final_message

# Example usage:
# input_message = "You have successfully downloaded the book information of the given category. Here is the data view token for the top 100 books in the HUMOR category: <data_retrieved=token>"
# result = process_message_and_replace_token(input_message)
# print(result)

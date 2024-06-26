import os
from dotenv import load_dotenv
load_dotenv()
from langchain_core.tools import tool
from BookInfo import BookInfo
import json
from uuid import uuid4
import chromadb
from time import sleep

# Load session ID from .env file
global session_id 
session_id = str(uuid4())

@tool
def googleAPI_retrieval(download_book_category_info: str) -> str:
    """
    This tool downloads book information of the given category and stores it in the database.
    """
    global session_id
    category = download_book_category_info
    book_info = BookInfo()
    book_info.category = category.strip().lower()
    book_info.get_top_books()
    with open(f"{session_id}.json", "w") as f:
        json.dump(book_info.processed_results, f)
        
    return "You have successfully downloaded the book information of the given category."

def search_db(keyword: str) -> str:
    """
    This function searches the database for the given keyword or name of the book and returns the information of the books that match the keyword and provides a data view token. keep default value of number_of_items as 5 if not specified.
    """
    pass

@tool
def present_book_info(number_of_items: str) -> str:
    """
    This tool extracts the information of the top number_of_items books in the database and gives you a data view token. This token will render at the user's end. Just place this token in the final response.
    """
    global session_id
    token = str(uuid4())
    
    # Check if the file exists
    while not os.path.exists(f"{session_id}.json"):
        sleep(1)
        
    with open(f"{session_id}.json", "r") as f:
        data = json.load(f)
        
    info = []
    for i in range(min(int(number_of_items), len(data))):
        info.append({
            "title": data[i]['title'],
            "authors": data[i]['authors'],
            "publisher": data[i]['publisher'],
            "publishedDate": data[i]['publishedDate'],
            "description": data[i]['description']
        })
    
    with open(f"{token}.json", "w") as f:
        json.dump(info, f)
    
    return f"<data_retrieved={token}>"

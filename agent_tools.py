import os
from dotenv import load_dotenv
load_dotenv()
from langchain_core.tools import tool
from BookInfo import BookInfo
import json
from uuid import uuid4
from time import sleep
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import CharacterTextSplitter
import chromadb
chroma_client = chromadb.Client()



# Load session ID from .env file
global session_id, db
session_id = "book_info"
vdb = chroma_client.get_or_create_collection("book_info")

@tool
def googleAPI_retrieval(download_book_category_info: str) -> str:
    """
    This tool downloads book information of the given category and stores it in the database.
    """
    category = download_book_category_info
    book_info = BookInfo()
    book_info.category = category.strip().lower()
    book_info.get_top_books()
    documentes = []
    ids = []
    metadata = []
    for item in book_info.processed_results:
        document = f"""Ranks: {item['rank']}
Title: {item['title']} 
Authors: {",".join(item['authors'])} 
Publisher: {item['publisher']} 
Published Date: {item['publishedDate']} 
Description:
{item['description']}"""
        documentes.append(document)
        ids.append(str(item['rank']))
        metadata.append({
            "title": item['title'],
            "authors": ",".join(item['authors']),
            "publisher": item['publisher'],
            "categories": ",".join(item['categories']),
        })
    vdb.add(documents=documentes, ids=ids, metadatas=metadata)

        
    with open(f"{session_id}.json", "w") as f:
        json.dump(book_info.processed_results, f)
    
    return "You have successfully downloaded the book information of the given category."

def search_db(keywords: str) -> str:
    """
    This function searches the database for the given keyword or name of the book and returns the information of the books.
    """
    docs = vdb.query(query_texts=[keywords], n_results=2)
    docs = docs.get('documents', [])
    return str(docs[0][0])

@tool
def present_book_info(number_of_items: str) -> str:
    """
    This tool extracts the information of the top number_of_items books in the database and gives you a data view token. This token will render at the user's end. Just place this token in the final response.
    """
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

if __name__ == "__main__":
    googleAPI_retrieval("fiction")
    print(search_db("funny"))
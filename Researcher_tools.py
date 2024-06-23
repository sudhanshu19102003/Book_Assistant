import json
from BookInfo import BookInfo
import chromadb as db
import pandas as pd


class Researcher_tools:
    def __init__(self):
        self.chroma_client = db.Client()
        self.book_info = BookInfo()
        self.book_collection = self.chroma_client.get_or_create_collection(name="book_info")
        self.aget_message = None
        try:
            with open ('tools.json') as f:
                self.tool_discreption = json.load(f)
        except FileNotFoundError as e:
            print(f"FileNotFoundError encountered: tools.json file not found or generated")
        
    def get_tool_discreption(self):
        index = 0
        tool_discreption = """Here are the tools available to you:"""
        if self.tool_discreption:
            for tool in self.tool_discreption:
                index += 1
                tool_discreption += f"""{index}. {tool['name']}
                                        Discreption:
                                        {tool['description']}
                                        Format:
                                        {tool['format']}
                                        Example:
                                        {tool['example']}
                                        """
            self.tool_discreption = tool_discreption
        
    def tool_selector(self):
        if "?action=" not in self.aget_message:
            self.tool_selected , self.arguements = None , None
        else:
            self.tool_selected = self.aget_message.split('?action=')[1].split(':')[0]
            self.arguements = self.aget_message.split('?action=')[1].split(':')[1].split(',')
        
        if self.tool_selected == 'fetch_data':
            if self.arguements:
                self.fetch_data()

        elif self.tool_selected == 'db_query':
            if self.arguements:
                self.db_query()

    def fetch_data(self)-> str:
        if self.arguements:
            category = self.arguements[0].split('=')[1]
            self.book_info.category = category
            self.book_info.get_top_books()
            documents = []
            metadatas = []
            ids = []
            for book in self.book_info.processed_results:
                authors = ", ".join(book['authors'])
                info = f"""
                        This book is ranked is {book["rank"]}
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
                'category': category
                }
                metadatas.append(metadata)

                ids.append(str(book['rank']))

        self.book_collection.add(
            documents = documents,
            ids = ids,
            metadatas = metadatas
            )
        
    def db_query(self):
        self.query = self.arguements[0].split('=')[1]
        results = self.book_collection.query(query_texts=self.query, n_results=3)
        paragraphs = ""
        for paragraph in results['documents'][0]:
            paragraphs += (paragraph + "\n")
        
            
if __name__ == '__main__':
    tools = Researcher_tools()
    tools.aget_message = "?action=fetch_data:category=fiction"
    tools.tool_selector()
    

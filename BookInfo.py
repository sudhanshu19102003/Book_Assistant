import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

class BookInfo:
    def __init__(self):
        self.url = 'https://www.googleapis.com/books/v1/volumes'
        self.api_key = os.getenv('GOOGLE_BOOKS_API_KEY')
        self.category = None
        self.results = None
        self.processed_results = []
        self.max_allowed_results = 40
        self.maxResults = 100
        self.start_index = 0
        self.no_of_books = None
        self.index=0

    def get_books(self):
        parameters = {
            'q': f'subject:{self.category}',
            'maxResults': min(self.no_of_books, self.max_allowed_results),
            'key': self.api_key,
            'orderBy': 'relevance',
            'startIndex': self.start_index
        }
        response = requests.get(self.url, params=parameters)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_top_books(self):
        for i in range(0, self.maxResults, self.max_allowed_results):
            self.start_index = i
            self.no_of_books = min(self.maxResults - i, self.max_allowed_results)
            self.results = self.get_books()
            self.process_results()


    def process_results(self):
        if self.results:
            try:
                for item in self.results.get('items', []):
                    self.index += 1
                    book = {
                        'rank': self.index,
                        'title': item['volumeInfo'].get('title', 'Unknown Title'),
                        'authors': item['volumeInfo'].get('authors', ['Unknown Author']),
                        'publisher': item['volumeInfo'].get('publisher', 'Unknown Publisher'),
                        'publishedDate': item['volumeInfo'].get('publishedDate', 'Unknown Date'),
                        'description': item['volumeInfo'].get('description', 'No Description'),
                        'categories': item['volumeInfo'].get('categories', ['Unknown Category']),
                    }
                    self.processed_results.append(book)
            except KeyError as e:
                print(f"KeyError encountered: {e}")

if __name__ == '__main__':
    book_info = BookInfo()
    book_info.category = 'Fiction'
    book_info.maxResults = 10
    book_info.get_top_books()

    if book_info.processed_results:
        for book in book_info.processed_results:
            print(f"{book['rank']} Title: {book['title']}")
import requests
from dotenv import load_dotenv
import os

load_dotenv()


class BookInfo:
    def __init__(self):
        self.url = "https://www.googleapis.com/books/v1/volumes"
        self.api_key = os.getenv("GOOGLE_BOOKS_API_KEY")
        self.category = None
        self.keywords = None
        self.search_type = (
            "keywords"  # Options: 'keywords', 'category', 'title', 'author', 'isbn'
        )
        self.results = None
        self.processed_results = []
        self.max_allowed_results = 40
        self.maxResults = 100
        self.start_index = 0
        self.no_of_books = None
        self.index = 0

    def build_query(self):
        """Build the search query based on search type and parameters."""
        if self.search_type == "category" and self.category:
            return f"subject:{self.category}"
        elif self.search_type == "keywords" and self.keywords:
            return self.keywords
        elif self.search_type == "title" and self.keywords:
            return f"intitle:{self.keywords}"
        elif self.search_type == "author" and self.keywords:
            return f"inauthor:{self.keywords}"
        elif self.search_type == "isbn" and self.keywords:
            return f"isbn:{self.keywords}"
        else:
            # Fallback to keywords or category
            return self.keywords if self.keywords else f"subject:{self.category}"

    def get_books(self):
        query = self.build_query()
        parameters = {
            "q": query,
            "maxResults": min(self.no_of_books, self.max_allowed_results),
            "key": self.api_key,
            "orderBy": "relevance",
            "startIndex": self.start_index,
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
                for item in self.results.get("items", []):
                    self.index += 1
                    volume_info = item.get("volumeInfo", {})

                    # Extract thumbnail URL from imageLinks
                    image_links = volume_info.get("imageLinks", {})
                    thumbnail = image_links.get(
                        "thumbnail", image_links.get("smallThumbnail", "")
                    )

                    book = {
                        "rank": self.index,
                        "title": volume_info.get("title", "Unknown Title"),
                        "authors": volume_info.get("authors", ["Unknown Author"]),
                        "publisher": volume_info.get("publisher", "Unknown Publisher"),
                        "publishedDate": volume_info.get(
                            "publishedDate", "Unknown Date"
                        ),
                        "description": volume_info.get("description", "No Description"),
                        "categories": volume_info.get(
                            "categories", ["Unknown Category"]
                        ),
                        "thumbnail": thumbnail,
                        "averageRating": volume_info.get("averageRating", None),
                        "ratingsCount": volume_info.get("ratingsCount", 0),
                        "pageCount": volume_info.get("pageCount", None),
                        "language": volume_info.get("language", "Unknown"),
                        "previewLink": volume_info.get("previewLink", ""),
                        "infoLink": volume_info.get("infoLink", ""),
                    }
                    self.processed_results.append(book)
            except KeyError as e:
                print(f"KeyError encountered: {e}")


if __name__ == "__main__":
    book_info = BookInfo()
    book_info.category = "Fiction"
    book_info.maxResults = 10
    book_info.get_top_books()

    if book_info.processed_results:
        for book in book_info.processed_results:
            print(f"{book['rank']} Title: {book['title']}")

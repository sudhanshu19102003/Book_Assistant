"""Google Books API service with Pydantic models."""

import requests
from typing import Any

from models.book import BookModel
from models.config import BookInfoConfig


class GoogleBooksService:
    """Fetches and processes book data from Google Books API."""

    def __init__(self, config: BookInfoConfig | None = None) -> None:
        self.config = config or BookInfoConfig()
        self._index = 0
        self._processed_results: list[BookModel] = []

    def _build_query(
        self,
        search_type: str,
        keywords: str | None = None,
        category: str | None = None,
    ) -> str:
        """Build the search query based on search type and parameters."""
        if search_type == "category" and category:
            return f"subject:{category}"
        if search_type == "keywords" and keywords:
            return keywords
        if search_type == "title" and keywords:
            return f"intitle:{keywords}"
        if search_type == "author" and keywords:
            return f"inauthor:{keywords}"
        if search_type == "isbn" and keywords:
            return f"isbn:{keywords}"
        return keywords if keywords else f"subject:{category or ''}"

    def _fetch_page(
        self,
        query: str,
        start_index: int,
        max_results: int,
    ) -> dict[str, Any]:
        """Fetch a single page of results from the API."""
        params = {
            "q": query,
            "maxResults": min(max_results, self.config.max_allowed_results),
            "key": self.config.api_key,
            "orderBy": "relevance",
            "startIndex": start_index,
        }
        response = requests.get(self.config.url, params=params)
        response.raise_for_status()
        return response.json()

    def _process_item(self, item: dict[str, Any]) -> BookModel:
        """Convert API item to BookModel."""
        volume_info = item.get("volumeInfo", {})
        image_links = volume_info.get("imageLinks", {}) or {}
        thumbnail = (
            image_links.get("thumbnail") or image_links.get("smallThumbnail") or ""
        )

        self._index += 1
        return BookModel(
            rank=self._index,
            title=volume_info.get("title", "Unknown Title"),
            authors=volume_info.get("authors", ["Unknown Author"]),
            publisher=volume_info.get("publisher", "Unknown Publisher"),
            publishedDate=volume_info.get("publishedDate", "Unknown Date"),
            description=volume_info.get("description", "No Description"),
            categories=volume_info.get("categories", ["Unknown Category"]),
            thumbnail=thumbnail,
            averageRating=volume_info.get("averageRating"),
            ratingsCount=volume_info.get("ratingsCount", 0),
            pageCount=volume_info.get("pageCount"),
            language=volume_info.get("language", "Unknown"),
            previewLink=volume_info.get("previewLink", ""),
            infoLink=volume_info.get("infoLink", ""),
        )

    def search(
        self,
        search_type: str = "keywords",
        keywords: str | None = None,
        category: str | None = None,
        max_results: int | None = None,
    ) -> list[BookModel]:
        """
        Search Google Books API and return list of BookModel.

        Args:
            search_type: One of 'keywords', 'category', 'title', 'author', 'isbn'
            keywords: Search keywords (for keywords, title, author, isbn)
            category: Category for category search
            max_results: Maximum results to fetch (default from config)

        Returns:
            List of BookModel instances
        """
        self._index = 0
        self._processed_results = []
        max_results = max_results or self.config.max_results

        query = self._build_query(search_type, keywords, category)
        if not query or query == "subject:":
            return []

        for start in range(0, max_results, self.config.max_allowed_results):
            batch_size = min(max_results - start, self.config.max_allowed_results)
            try:
                results = self._fetch_page(query, start, batch_size)
            except requests.RequestException:
                break

            items = results.get("items") or []
            if not items:
                break

            for item in items:
                try:
                    book = self._process_item(item)
                    self._processed_results.append(book)
                except (KeyError, ValueError):
                    continue

        return self._processed_results

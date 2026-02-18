"""Core book data models."""

from typing import Optional
from pydantic import BaseModel, Field


class BookModel(BaseModel):
    """Main book data model with all fields."""

    rank: int
    title: str = "Unknown Title"
    authors: list[str] = Field(default_factory=lambda: ["Unknown Author"])
    publisher: str = "Unknown Publisher"
    publishedDate: str = "Unknown Date"
    description: str = "No Description"
    categories: list[str] = Field(default_factory=lambda: ["Unknown Category"])
    thumbnail: str = ""
    averageRating: Optional[float] = None
    ratingsCount: int = 0
    pageCount: Optional[int] = None
    language: str = "Unknown"
    previewLink: str = ""
    infoLink: str = ""

    model_config = {"extra": "allow"}

    @classmethod
    def from_dict(cls, data: dict) -> "BookModel":
        """Create BookModel from dictionary (backward compatible with existing JSON)."""
        return cls(
            rank=data.get("rank", 0),
            title=data.get("title", "Unknown Title"),
            authors=data.get("authors", ["Unknown Author"]),
            publisher=data.get("publisher", "Unknown Publisher"),
            publishedDate=data.get("publishedDate", "Unknown Date"),
            description=data.get("description", "No Description"),
            categories=data.get("categories", ["Unknown Category"]),
            thumbnail=data.get("thumbnail", ""),
            averageRating=data.get("averageRating"),
            ratingsCount=data.get("ratingsCount", 0),
            pageCount=data.get("pageCount"),
            language=data.get("language", "Unknown"),
            previewLink=data.get("previewLink", ""),
            infoLink=data.get("infoLink", ""),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump(exclude_none=False, exclude_defaults=False)


class SearchMetadata(BaseModel):
    """Search query metadata."""

    search_id: str
    search_type: str = "keywords"
    search_query: str = ""

    model_config = {"extra": "forbid"}


class BookSearchResult(BaseModel):
    """Wrapper for search results with metadata."""

    books: list[BookModel]
    metadata: SearchMetadata

    model_config = {"extra": "forbid"}

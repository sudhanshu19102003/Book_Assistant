"""Configuration models."""

from typing import Optional
from pydantic import BaseModel, Field

import os
from dotenv import load_dotenv

load_dotenv()


class BookInfoConfig(BaseModel):
    """Configuration for Google Books API service."""

    url: str = "https://www.googleapis.com/books/v1/volumes"
    api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GOOGLE_BOOKS_API_KEY"))
    max_allowed_results: int = 40
    max_results: int = 100
    start_index: int = 0

    model_config = {"extra": "forbid"}


class AppConfig(BaseModel):
    """Application-wide configuration."""

    book_info: BookInfoConfig = Field(default_factory=BookInfoConfig)
    chroma_collection_name: str = "book_info"

    model_config = {"extra": "forbid"}

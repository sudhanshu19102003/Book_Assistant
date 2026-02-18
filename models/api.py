"""API response models for Google Books API."""

from typing import Optional, Any
from pydantic import BaseModel, Field


class ImageLinks(BaseModel):
    """Thumbnail URLs from Google Books API."""

    smallThumbnail: Optional[str] = None
    thumbnail: Optional[str] = None

    model_config = {"extra": "allow"}


class VolumeInfo(BaseModel):
    """Volume information from Google Books API response."""

    title: Optional[str] = None
    authors: Optional[list[str]] = None
    publisher: Optional[str] = None
    publishedDate: Optional[str] = None
    description: Optional[str] = None
    categories: Optional[list[str]] = None
    imageLinks: Optional[ImageLinks | dict[str, Any]] = None
    averageRating: Optional[float] = None
    ratingsCount: Optional[int] = None
    pageCount: Optional[int] = None
    language: Optional[str] = None
    previewLink: Optional[str] = None
    infoLink: Optional[str] = None

    model_config = {"extra": "allow"}


class GoogleBooksItem(BaseModel):
    """Single item from Google Books API response."""

    volumeInfo: Optional[VolumeInfo | dict[str, Any]] = None

    model_config = {"extra": "allow"}


class GoogleBooksAPIResponse(BaseModel):
    """Response structure from Google Books API."""

    items: Optional[list[GoogleBooksItem | dict[str, Any]]] = None
    totalItems: Optional[int] = None

    model_config = {"extra": "allow"}

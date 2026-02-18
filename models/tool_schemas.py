"""Tool input/output schemas for validation."""

from typing import Literal
from pydantic import BaseModel, Field, field_validator


SearchType = Literal["keywords", "category", "title", "author", "isbn"]


class GoogleAPIRetrievalInput(BaseModel):
    """Input schema for googleAPI_retrieval tool."""

    search_query: str = Field(..., min_length=1)
    search_type: SearchType = "keywords"

    model_config = {"extra": "forbid"}

    @field_validator("search_query")
    @classmethod
    def search_query_stripped(cls, v: str) -> str:
        return v.strip()

    @field_validator("search_type", mode="before")
    @classmethod
    def search_type_normalize(cls, v: str) -> str:
        normalized = str(v).strip().lower()
        if normalized not in ["keywords", "category", "title", "author", "isbn"]:
            return "keywords"
        return normalized


class PresentBookInfoInput(BaseModel):
    """Input schema for present_book_info tool."""

    search_id: str = Field(..., min_length=1)
    number_of_items: str = "10"

    model_config = {"extra": "forbid"}

    @field_validator("number_of_items")
    @classmethod
    def validate_number(cls, v: str) -> str:
        try:
            n = int(v)
            return str(max(1, min(n, 100)))
        except ValueError:
            return "10"


class SearchDBInput(BaseModel):
    """Input schema for search_db tool."""

    keywords: str = Field(..., min_length=1)
    num_results: str = "3"

    model_config = {"extra": "forbid"}

    @field_validator("num_results")
    @classmethod
    def validate_num_results(cls, v: str) -> str:
        try:
            n = int(v)
            return str(max(1, min(n, 10)))
        except ValueError:
            return "3"


class GetBookByRankInput(BaseModel):
    """Input schema for get_book_by_rank tool."""

    search_id: str = Field(..., min_length=1)
    rank: str = Field(..., min_length=1)

    model_config = {"extra": "forbid"}

    @field_validator("rank")
    @classmethod
    def validate_rank(cls, v: str) -> str:
        try:
            n = int(v)
            if n < 1:
                raise ValueError("Rank must be positive")
            return str(n)
        except ValueError:
            raise ValueError("Rank must be a valid positive integer")

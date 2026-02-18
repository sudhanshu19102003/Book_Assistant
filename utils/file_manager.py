"""File I/O operations for JSON data."""

import json
from pathlib import Path
from typing import Any

from models.book import BookModel


class FileManager:
    """Handles reading and writing JSON files for book data."""

    def __init__(self, base_path: Path | str | None = None) -> None:
        self.base_path = Path(base_path) if base_path else Path.cwd()

    def _resolve_path(self, filename: str) -> Path:
        """Resolve filename to full path."""
        return self.base_path / filename

    def read_json(self, filename: str) -> list[dict[str, Any]] | dict[str, Any]:
        """
        Read JSON from file.

        Returns:
            Parsed JSON data (list or dict)

        Raises:
            FileNotFoundError: If file does not exist
            json.JSONDecodeError: If file contains invalid JSON
        """
        path = self._resolve_path(filename)
        with open(path, "r") as f:
            return json.load(f)

    def write_json(
        self,
        filename: str,
        data: list[dict[str, Any]] | dict[str, Any] | list[BookModel],
    ) -> None:
        """
        Write data to JSON file.

        Args:
            filename: Target filename
            data: Data to serialize (list of dicts, dict, or list of BookModel)
        """
        path = self._resolve_path(filename)
        if isinstance(data, list) and data and isinstance(data[0], BookModel):
            serializable = [b.to_dict() for b in data]
        else:
            serializable = data
        with open(path, "w") as f:
            json.dump(serializable, f, indent=2)

    def file_exists(self, filename: str) -> bool:
        """Check if file exists."""
        return self._resolve_path(filename).exists()

    def read_books_json(self, filename: str) -> list[dict[str, Any]]:
        """
        Read JSON file expected to contain list of book objects.

        Returns:
            List of book dictionaries

        Raises:
            FileNotFoundError: If file does not exist
            json.JSONDecodeError: If file contains invalid JSON
        """
        data = self.read_json(filename)
        if not isinstance(data, list):
            raise ValueError(f"Expected list of books, got {type(data)}")
        return data

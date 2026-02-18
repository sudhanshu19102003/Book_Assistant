"""HTML rendering component for book tables using Jinja2 templates."""

import json
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader, select_autoescape

if TYPE_CHECKING:
    from models.book import BookModel

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def _html_escape(text: str) -> str:
    """Escape text for HTML display."""
    return text.replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def _prepare_book_for_template(book: "BookModel", index: int) -> dict:
    """Convert BookModel to template-friendly dict with escaped values."""
    authors = ", ".join(book.authors)
    return {
        "index": index,
        "title_html": _html_escape(book.title),
        "authors_html": _html_escape(authors),
        "publisher_html": _html_escape(book.publisher),
        "published_date": book.publishedDate,
        "cover_html": (
            f'<img src="{book.thumbnail}" alt="{_html_escape(book.title)}" class="book-cover">'
            if book.thumbnail
            else '<div class="no-cover">No Cover</div>'
        ),
        # For data attributes (already HTML-escaped by Jinja autoescape)
        "title": book.title,
        "authors": authors,
        "publisher": book.publisher,
        "description": book.description,
        "thumbnail": book.thumbnail or "",
    }


class BookTableRenderer:
    """Renders book data as HTML tables using Jinja2 templates."""

    def __init__(self, templates_dir: Path | None = None) -> None:
        self.templates_dir = templates_dir or TEMPLATES_DIR
        self._env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def _load_styles(self) -> str:
        """Load and return CSS styles."""
        styles_path = self.templates_dir / "styles.css"
        return f"<style>\n{styles_path.read_text()}\n</style>"

    def _load_script(self, unique_id: str) -> str:
        """Load JavaScript and inject unique_id."""
        script_path = self.templates_dir / "book_table.js"
        script_content = script_path.read_text()
        # Replace all occurrences of the placeholder
        return script_content.replace("___UNIQUE_ID__", unique_id)

    def render(
        self,
        books: list["BookModel"],
        unique_id: str,
        include_styles: bool = False,
    ) -> str:
        """
        Render a list of books as HTML table with interactive details panel.

        Args:
            books: List of BookModel instances
            unique_id: Unique identifier for this table (used for JS function names)
            include_styles: If True, include CSS in output. Set False when multiple
                tables are rendered - include styles once at the start.

        Returns:
            HTML string for the book table
        """
        safe_id = unique_id.replace("-", "_")
        prepared_books = [
            _prepare_book_for_template(book, i + 1) for i, book in enumerate(books)
        ]

        html_template = self._env.get_template("book_table.html")
        html_output = html_template.render(books=prepared_books, unique_id=safe_id)

        script = self._load_script(safe_id)
        script_tag = f"<script>\n{script}\n</script>"

        if include_styles:
            return self._load_styles() + html_output + script_tag
        return html_output + script_tag

    def render_from_dicts(
        self,
        books_data: list[dict],
        unique_id: str,
        include_styles: bool = False,
    ) -> str:
        """
        Render books from list of dicts (backward compatible with JSON files).

        Args:
            books_data: List of book dictionaries
            unique_id: Unique identifier for this table
            include_styles: If True, include CSS in output

        Returns:
            HTML string for the book table
        """
        from models.book import BookModel

        books = [BookModel.from_dict(b) for b in books_data]
        return self.render(books, unique_id, include_styles)

"""LangChain tools for book search and retrieval."""

import json
from uuid import uuid4

from langchain_core.tools import tool
import chromadb
import logging

from dotenv import load_dotenv

from models.book import BookModel
from models.tool_schemas import (
    GoogleAPIRetrievalInput,
    PresentBookInfoInput,
    SearchDBInput,
    GetBookByRankInput,
)
from services.google_books_service import GoogleBooksService
from utils.file_manager import FileManager

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("tool_logs.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

chroma_client = chromadb.Client()
vdb = chroma_client.get_or_create_collection("book_info")

_file_manager = FileManager()


def _validate_google_input(search_query: str, search_type: str) -> GoogleAPIRetrievalInput:
    """Validate and return sanitized input for googleAPI_retrieval."""
    return GoogleAPIRetrievalInput(search_query=search_query, search_type=search_type)


def _validate_present_input(search_id: str, number_of_items: str) -> PresentBookInfoInput:
    """Validate and return sanitized input for present_book_info."""
    return PresentBookInfoInput(search_id=search_id, number_of_items=number_of_items)


def _validate_search_input(keywords: str, num_results: str) -> SearchDBInput:
    """Validate and return sanitized input for search_db."""
    return SearchDBInput(keywords=keywords, num_results=num_results)


def _validate_rank_input(search_id: str, rank: str) -> GetBookByRankInput:
    """Validate and return sanitized input for get_book_by_rank."""
    return GetBookByRankInput(search_id=search_id, rank=rank)


def _book_to_document(book: BookModel) -> str:
    """Create rich document text for vector database."""
    return f"""Rank: {book.rank}
Title: {book.title}
Authors: {", ".join(book.authors)}
Publisher: {book.publisher}
Published Date: {book.publishedDate}
Categories: {", ".join(book.categories)}
Rating: {book.averageRating or 'N/A'} ({book.ratingsCount} ratings)
Pages: {book.pageCount or 'N/A'}
Language: {book.language}

Description:
{book.description}"""


@tool
def googleAPI_retrieval(search_query: str, search_type: str = "keywords") -> str:
    """
    This tool downloads book information based on flexible search criteria and stores it in the database.
    Returns a unique search_id that can be used with present_book_info to display these specific results.

    Args:
        search_query: The search term - can be a single term or multiple terms combined
            - For keywords: You can combine multiple keywords (e.g., "science fiction adventure")
            - For categories: You can combine multiple categories (e.g., "fiction mystery")
            - For other types: Single values work best
        search_type: Type of search - options are:
            - "keywords" (default): General keyword search across all fields - best for combining multiple terms
            - "category": Search by book category/subject - can combine multiple categories
            - "title": Search specifically in book titles
            - "author": Search by author name
            - "isbn": Search by ISBN number

    Returns:
        A message containing the search_id that should be used with present_book_info to display results

    Examples:
        - googleAPI_retrieval("artificial intelligence machine learning", "keywords")
        - googleAPI_retrieval("science fiction adventure", "keywords")
        - googleAPI_retrieval("fiction mystery thriller", "category")
        - googleAPI_retrieval("Stephen King", "author")
        - googleAPI_retrieval("Harry Potter", "title")
    """
    try:
        validated = _validate_google_input(search_query, search_type)
    except Exception as e:
        logger.warning(f"googleAPI_retrieval validation error: {e}")
        validated = GoogleAPIRetrievalInput(search_query=search_query.strip(), search_type="keywords")

    logger.info(
        f"googleAPI_retrieval called with search_query='{validated.search_query}', "
        f"search_type='{validated.search_type}'"
    )
    search_id = str(uuid4())

    service = GoogleBooksService()
    books = service.search(
        search_type=validated.search_type,
        keywords=validated.search_query if validated.search_type != "category" else None,
        category=validated.search_query.lower() if validated.search_type == "category" else None,
    )

    if not books:
        return (
            f"No books found for the search query: '{validated.search_query}' "
            f"with search type: '{validated.search_type}'"
        )

    documents = []
    ids = []
    metadata = []

    for book in books:
        documents.append(_book_to_document(book))
        ids.append(str(uuid4()))
        metadata.append({
            "rank": str(book.rank),
            "title": book.title,
            "authors": ",".join(book.authors),
            "publisher": book.publisher,
            "categories": ",".join(book.categories),
            "rating": str(book.averageRating or ""),
            "search_query": validated.search_query,
            "search_type": validated.search_type,
            "search_id": search_id,
        })

    vdb.add(documents=documents, ids=ids, metadatas=metadata)

    books_data = [b.to_dict() for b in books]
    _file_manager.write_json(f"search_{search_id}.json", books_data)

    result = (
        f"Successfully downloaded {len(books)} books for search query: '{validated.search_query}' "
        f"(search type: '{validated.search_type}'). Search ID: {search_id}"
    )
    logger.info(f"googleAPI_retrieval result: {result}")
    return result


@tool
def search_db(keywords: str, num_results: str = "3") -> str:
    """
    This tool searches the vector database for books matching the given keywords or description.
    It uses semantic search to find relevant books based on meaning, not just exact matches.

    Args:
        keywords: Search keywords or description (e.g., "funny adventure books", "mystery thriller", "books about AI")
        num_results: Number of results to return (default: "3", max: "10")

    Returns:
        Formatted information about the matching books
    """
    try:
        validated = _validate_search_input(keywords, num_results)
    except Exception:
        validated = SearchDBInput(keywords=keywords, num_results="3")

    logger.info(
        f"search_db called with keywords='{validated.keywords}', num_results='{validated.num_results}'"
    )
    n = int(validated.num_results)

    results = vdb.query(query_texts=[validated.keywords], n_results=n)
    documents = results.get("documents", [[]])
    metadatas = results.get("metadatas", [[]])

    if not documents or not documents[0]:
        result = (
            f"No books found matching: '{validated.keywords}'. "
            "Please download books first using googleAPI_retrieval."
        )
        logger.info(f"search_db result: {result}")
        return result

    output = f"Found {len(documents[0])} books matching '{validated.keywords}':\n\n"
    for i, (doc, meta) in enumerate(zip(documents[0], metadatas[0]), 1):
        output += f"--- Result {i} ---\n"
        output += f"Title: {meta.get('title', 'Unknown')}\n"
        output += f"Authors: {meta.get('authors', 'Unknown')}\n"
        output += f"Rating: {meta.get('rating', 'N/A')}\n"
        output += f"Categories: {meta.get('categories', 'Unknown')}\n"
        output += f"\nPreview:\n{doc[:300]}...\n\n"

    logger.info(f"search_db result: Found {len(documents[0])} books")
    return output


@tool
def present_book_info(search_id: str, number_of_items: str = "10") -> str:
    """
    This tool extracts the information of the top number_of_items books from a specific search and gives you a data view token.
    This token will render at the user's end. Just place this token in the final response.

    You can call this tool multiple times with different search_ids to display results from multiple searches.
    Each search_id comes from a googleAPI_retrieval call.

    Args:
        search_id: The unique search ID returned by googleAPI_retrieval (required)
        number_of_items: Number of books to display (default: "10")

    Returns:
        A token in the format <data_retrieved=TOKEN> that will render as a table at the user's end

    Example:
        After calling googleAPI_retrieval which returns "Search ID: abc-123",
        call present_book_info("abc-123", "5") to display 5 books from that search.
    """
    try:
        validated = _validate_present_input(search_id, number_of_items)
    except Exception:
        validated = PresentBookInfoInput(search_id=search_id, number_of_items="10")

    logger.info(
        f"present_book_info called with search_id='{validated.search_id}', "
        f"number_of_items='{validated.number_of_items}'"
    )
    token = str(uuid4())
    search_file = f"search_{validated.search_id}.json"

    if not _file_manager.file_exists(search_file):
        return (
            f"Error: Search ID '{validated.search_id}' not found. "
            "Please use a valid search_id from a googleAPI_retrieval call."
        )

    data = _file_manager.read_books_json(search_file)
    count = min(int(validated.number_of_items), len(data))
    info = [BookModel.from_dict(data[i]).to_dict() for i in range(count)]

    _file_manager.write_json(f"{token}.json", info)

    result = f"<data_retrieved={token}>"
    logger.info(
        f"present_book_info result: Generated token {token} for {len(info)} items "
        f"from search {validated.search_id}"
    )
    return result


@tool
def get_book_by_rank(search_id: str, rank: str) -> str:
    """
    This tool retrieves detailed information about a specific book by its rank/position number from a specific search.

    Args:
        search_id: The unique search ID returned by googleAPI_retrieval
        rank: The rank/position of the book (e.g., "1" for first book, "10" for tenth book)

    Returns:
        Detailed information about the book including title, authors, publisher, published date, description, and categories.

    Example:
        get_book_by_rank("abc-123", "5") - Gets the 5th book from search "abc-123"
    """
    try:
        validated = _validate_rank_input(search_id, rank)
    except Exception as e:
        logger.warning(f"get_book_by_rank validation error: {e}")
        return "Invalid rank format. Please provide a valid number."

    logger.info(
        f"get_book_by_rank called with search_id='{validated.search_id}', rank='{validated.rank}'"
    )
    rank_num = int(validated.rank)
    search_file = f"search_{validated.search_id}.json"

    if not _file_manager.file_exists(search_file):
        return (
            f"Error: Search ID '{validated.search_id}' not found. "
            "Please use a valid search_id from a googleAPI_retrieval call."
        )

    try:
        data = _file_manager.read_books_json(search_file)
    except (ValueError, json.JSONDecodeError) as e:
        logger.error(f"get_book_by_rank error: {e}")
        return f"Error reading search data: {str(e)}"

    if rank_num < 1 or rank_num > len(data):
        return f"Invalid rank. Please provide a rank between 1 and {len(data)}."

    book = BookModel.from_dict(data[rank_num - 1])
    book_info = f"""Book Rank: {book.rank}
Title: {book.title}
Authors: {", ".join(book.authors)}
Publisher: {book.publisher}
Published Date: {book.publishedDate}
Categories: {", ".join(book.categories)}

Description:
{book.description}"""

    logger.info(
        f"get_book_by_rank result: Retrieved book '{book.title}' at rank {validated.rank} "
        f"from search {validated.search_id}"
    )
    return book_info


if __name__ == "__main__":
    # Example 1: Search by keywords
    print(
        googleAPI_retrieval.invoke(
            {
                "search_query": "artificial intelligence machine learning",
                "search_type": "keywords",
            }
        )
    )

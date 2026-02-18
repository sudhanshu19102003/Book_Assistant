# Book Assistant

An intelligent book search assistant powered by AI agents that retrieves and displays book information from Google Books API with an interactive Streamlit interface.

https://github.com/sudhanshu19102003/LLM_agent_books/assets/78022236/a001d579-1c09-4830-964b-e719b200782e

## Features

- **AI-Powered Search** - Natural language queries to find books by title, author, category, or keywords
- **Google Books Integration** - Real-time data retrieval from Google Books API
- **Vector Search** - Semantic search through stored book data using ChromaDB
- **Interactive UI** - Clean Streamlit chat interface with dynamic book tables
- **Smart Caching** - Stores retrieved books locally for faster subsequent searches
- **Multi-Search Display** - View results from multiple searches simultaneously

## Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd Book_Assistant
```

2. **Install dependencies**
```bash
uv sync
```
get uv from https://docs.astral.sh/uv/getting-started/installation/

3. **Set up environment variables**
Create a `.env` file with your API keys:
```
ANTHROPIC_API_KEY=your_anthropic_key_here
```

4. **Run the application**
```bash
uv run streamlit run main.py
```

## Key Libraries

- **LangChain** - Agent orchestration and tool management
- **LangGraph** - State graph for workflow management
- **Anthropic Claude** - LLM for natural language understanding
- **ChromaDB** - Vector database for semantic search
- **Streamlit** - Interactive web interface
- **Google Books API** - Book data source

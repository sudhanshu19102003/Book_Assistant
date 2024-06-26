# BookAssistant README

## Overview

The BookAssistant is designed to interact with users, retrieve book information using various tools, and present structured responses. It leverages a language model (ChatAnthropic), Vector database, and a LangChain state graph to efficiently manage interactions and data flow.

https://github.com/sudhanshu19102003/LLM_agent_books/assets/78022236/a001d579-1c09-4830-964b-e719b200782e

## Components

### 1. Initialization and Setup

The `BookAssistant` class initializes several components:

- **Language Model:** Uses ChatAnthropic.
- **Tools:** Defines tools (`googleAPI_retrieval`, `present_book_info`, `search_db`) for retrieving and presenting book information.

### 2. Graph Construction

- **State Graph:** Constructs a state graph to manage state transitions and tool interactions.
  
  - **Nodes and Edges:**
    - Adds nodes for an assistant (handling user interactions) and tools (containing tools and error handling).
    - Establishes conditional edges and entry points (assistant) within the graph.

### 3. Tools

- `googleAPI_retrieval`: This class acts as a wrapper for retrieving data from the Google Books API. The fetched data is stored in both JSON format and a Chroma database, facilitating efficient extraction and search operations.

- `present_book_info`: This function extracts data from the JSON file and renders it in the chat interface using a token, enhancing data presentation reliability and reducing model token usage.

- `search_db`: Enables vector similarity search on retrieved data, enhancing search capabilities based on content similarity.

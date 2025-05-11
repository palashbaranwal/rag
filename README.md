# RAG History Search Extension

A Chrome extension that allows you to search through your browsing history using RAG (Retrieval-Augmented Generation). The extension provides semantic search capabilities and highlights relevant content on web pages.

## Features

- Semantic search through browsing history
- Similarity scoring for search results
- Clean and intuitive user interface

## Project Structure

```
Session_7_RAG_Memory/S7_Asgn/
├── extension/                 # Chrome extension files
│   ├── manifest.json         # Extension configuration
│   ├── popup.html           # Extension popup interface
│   ├── popup.js             # Popup functionality
│   ├── background.js        # Background service worker
│   ├── content.js           # Content script for highlighting
│   └── icons/               # Extension icons
├── api_server.py            # Flask server for RAG functionality
├── memory.py               # Memory management
├── perception.py           # Query intent extraction
├── decision.py             # Search plan generation
├── action.py               # Search execution
├── models.py               # Data models
├── logger_config.py        # Logging configuration
├── create_embedding.py     # Embedding creation utility
└── requirements.txt        # Python dependencies
```

## Agentic Architecture

The system follows an agentic architecture with the following components:

### 1. Memory (`memory.py`)
- Manages the vector store of embeddings
- Handles FAISS index for efficient similarity search
- Stores metadata about each chunk of text
- Provides methods for retrieving similar content

### 2. Perception (`perception.py`)
- Extracts user intent from search queries
- Processes and normalizes input text
- Identifies key concepts and search parameters
- Prepares query for the decision-making phase

### 3. Decision (`decision.py`)
- Generates search plans based on user intent
- Determines whether to show history or perform search
- Creates optimized search queries
- Handles result ranking and scoring

### 4. Action (`action.py`)
- Executes the search plan
- Manages search history
- Formats and returns results
- Handles error cases and edge conditions

## System Flow

1. **Extension Initiation**
   - User clicks extension icon
   - `popup.html` loads the search interface
   - `popup.js` initializes event listeners

2. **Search Request**
   - User enters search query
   - `popup.js` sends message to `background.js`
   - `background.js` forwards request to RAG server

3. **RAG Server Processing**
   - `api_server.py` receives request
   - Calls `perception.py` to extract intent
   - `decision.py` generates search plan
   - `memory.py` performs similarity search
   - `action.py` executes search and formats results

4. **Result Handling**
   - Results sent back to `background.js`
   - `popup.js` displays results in interface
   - `content.js` handles text highlighting

## Recent Updates

### Extension Development
- Created Chrome extension with popup interface
- Implemented background service worker for API communication
- Added content script for text highlighting
- Integrated with RAG server for semantic search

### API Server
- Added proper error handling
- Implemented CORS support
- Added logging functionality
- Improved response formatting
- Added similarity scoring

### Code Organization
- Separated embedding creation into `create_embedding.py`
- Implemented comprehensive logging across all components
- Added proper error handling throughout the application
- Created `.gitignore` for better version control

### Features Added
1. Chrome Extension:
   - Search interface in popup
   - Automatic URL opening
   - Text highlighting in pages
   - Similarity score display
   - Error handling and user feedback

2. RAG System:
   - Semantic search capabilities
   - Query intent extraction
   - Search plan generation
   - Result ranking and scoring

## Setup Instructions

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the RAG server:
   ```bash
   python api_server.py
   ```

3. Load the Chrome extension:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the `extension` folder

## Usage

1. Click the extension icon in Chrome
2. Enter your search query
3. View the top three most relevant results
4. Click on any result to open the page with highlighted text

## Dependencies

### Python
- Flask
- FAISS
- NumPy
- Other dependencies listed in `requirements.txt`

### Chrome Extension
- Manifest V3
- Chrome Extension APIs
- Modern JavaScript (ES6+)

## Notes

- The extension requires the RAG server to be running on `http://localhost:5000`
- Make sure to generate embeddings before using the search functionality
- The extension uses semantic search, so results may differ from traditional keyword search

## Future Improvements

- Add support for more search parameters
- Implement result filtering
- Add search history
- Improve text highlighting accuracy
- Add support for different embedding models 
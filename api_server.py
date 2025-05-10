from flask import Flask, request, jsonify
from flask_cors import CORS
from memory import MemoryManager
from perception import extract_perception
from decision import generate_search_plan
from action import execute_search
from logger_config import setup_logger
from models import ChunkMetadata
import json
import numpy as np
import faiss

# Set up logger
logger = setup_logger("api_server")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize memory manager
memory = None

def initialize_memory():
    """Initialize the memory manager with pre-computed embeddings."""
    global memory
    try:
        memory = MemoryManager()
        # Load embeddings from file
        with open("embeddings.json", "r") as f:
            data = json.load(f)
            memory.embeddings = [np.array(emb) for emb in data["embeddings"]]
            memory.metadata = [ChunkMetadata(**meta) for meta in data["metadata"]]
            
            # Initialize FAISS index
            if memory.embeddings:
                memory.index = faiss.IndexFlatL2(len(memory.embeddings[0]))
                memory.index.add(np.stack(memory.embeddings))
        
        logger.info(f"Successfully loaded {len(memory.metadata)} chunks")
    except Exception as e:
        logger.error(f"Error initializing memory: {str(e)}")
        raise

@app.route('/search', methods=['POST'])
def search():
    """Handle search requests from the extension."""
    try:
        data = request.get_json()
        query = data.get('query')
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        logger.info(f"Received search request: {query}")
        
        # Extract intent
        intent = extract_perception(query)
        
        # Generate search plan
        search_query, show_history = generate_search_plan(intent, memory)
        
        if show_history:
            return jsonify({"error": "History requests not supported in extension"}), 400
        
        # Execute search
        response = execute_search(search_query, memory)
        
        # Format results for the extension
        results = [
            {
                "url": result.url,
                "content": result.content,
                "similarity_score": result.similarity_score
            }
            for result in response.results
        ]
        
        logger.info(f"Returning {len(results)} results")
        return jsonify({"results": results})
    
    except Exception as e:
        logger.error(f"Error processing search request: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        initialize_memory()
        app.run(port=5000)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}") 
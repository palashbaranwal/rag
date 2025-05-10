import os
from pathlib import Path
from memory import MemoryManager
from perception import extract_perception
from decision import generate_search_plan
from action import execute_search, show_search_history
from models import ChunkMetadata
import json
import numpy as np
import faiss
from logger_config import setup_logger

# Set up logger
logger = setup_logger("main")

def chunk_text(text: str, size: int = 50, overlap: int = 10) -> list:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunk = " ".join(words[i:i+size])
        if chunk:
            chunks.append(chunk)
    return chunks

def initialize_memory():
    """Initialize memory with scraped texts."""
    memory = MemoryManager()
    scraped_texts_path = Path("scraped_texts")
    
    print("Processing scraped history files...")
    for file in scraped_texts_path.glob("*.txt"):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            
            # Extract URL
            url = None
            for line in content.split('\n'):
                if line.startswith('URL: '):
                    url = line[5:].strip()
                    break
            
            if not url:
                continue
            
            # Get actual content
            content_lines = content.split('\n\n', 1)
            if len(content_lines) > 1:
                actual_content = content_lines[1]
                
                # Create chunks
                chunks = chunk_text(actual_content)
                
                # Process each chunk
                for idx, chunk in enumerate(chunks):
                    metadata = ChunkMetadata(
                        url=url,
                        chunk=chunk,
                        chunk_id=f"{file.stem}_{idx}"
                    )
                    embedding = memory.get_embedding(chunk)
                    memory.add_chunk(metadata, embedding)
        
        print(f"Processed: {file.name}")
    
    return memory

def load_embeddings():
    """Load pre-computed embeddings and metadata."""
    memory = MemoryManager()
    embeddings_file = "embeddings.json"
    
    if not os.path.exists(embeddings_file):
        logger.error("embeddings.json not found! Please run create_embedding.py first.")
        return None
    
    try:
        with open(embeddings_file, 'r') as f:
            data = json.load(f)
            
        # Load metadata
        for meta_dict in data["metadata"]:
            memory.metadata.append(ChunkMetadata(**meta_dict))
        
        # Load embeddings
        memory.embeddings = [np.array(emb) for emb in data["embeddings"]]
        
        # Initialize FAISS index
        if memory.embeddings:
            memory.index = faiss.IndexFlatL2(len(memory.embeddings[0]))
            memory.index.add(np.stack(memory.embeddings))
        
        logger.info(f"Successfully loaded {len(memory.metadata)} chunks")
        return memory
    
    except Exception as e:
        logger.error(f"Error loading embeddings: {str(e)}")
        return None

def main():
    logger.info("Starting search application")
    
    # Load pre-computed embeddings
    memory = load_embeddings()
    
    if not memory or not memory.metadata:
        logger.error("Failed to initialize memory. Exiting...")
        return
    
    logger.info("Entering main interaction loop")
    
    # Main interaction loop
    while True:
        try:
            query = input("\n🔍 Enter your search query (or 'quit' to exit): ")
            if query.lower() == 'quit':
                logger.info("User requested exit")
                break
            
            logger.info(f"Processing query: {query}")
            
            # Extract intent
            intent = extract_perception(query)
            logger.debug(f"Extracted intent: {intent}")
            
            # Generate search plan
            search_query, show_history = generate_search_plan(intent, memory)
            
            if show_history:
                # Show search history
                logger.info("Showing search history")
                history = show_search_history(memory)
                print("\n📚 Recent Searches:")
                for item in history:
                    print(f"\nQuery: {item['query']}")
                    print(f"Time: {item['timestamp']}")
                    print(f"Results: {item['num_results']}")
                    print("URLs:")
                    for url in item['urls']:
                        print(f"  - {url}")
            else:
                # Execute search
                logger.info(f"Executing search with query: {search_query.query_text}")
                response = execute_search(search_query, memory)
                
                print("\n📚 Search Results:")
                for i, result in enumerate(response.results, 1):
                    print(f"\n{i}. URL: {result.url}")
                    print(f"   Content: {result.content}")
                
                logger.info(f"Search completed with {len(response.results)} results")
        
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            print("An error occurred while processing your query. Please try again.")

    logger.info("Application shutdown")

if __name__ == "__main__":
    main() 
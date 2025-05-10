import os
from pathlib import Path
from memory import MemoryManager
from perception import extract_perception
from decision import generate_search_plan
from action import execute_search, show_search_history
from models import ChunkMetadata
import time

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

def main():
    # Initialize memory
    memory = initialize_memory()
    
    if not memory.metadata:
        print("No files found in scraped_texts directory!")
        return
    
    print(f"\n✅ Indexed {len(memory.metadata)} chunks")
    
    # Main interaction loop
    while True:
        query = input("\n🔍 Enter your search query (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        
        # Extract intent
        intent = extract_perception(query)
        
        # Generate search plan
        search_query, show_history = generate_search_plan(intent, memory)
        
        if show_history:
            # Show search history
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
            response = execute_search(search_query, memory)
            
            print("\n📚 Search Results:")
            for i, result in enumerate(response.results, 1):
                print(f"\n{i}. URL: {result.url}")
                print(f"   Content: {result.content}")

if __name__ == "__main__":
    main() 
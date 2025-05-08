import os
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import time

# Configuration
CHUNK_SIZE = 50  # Words per chunk
CHUNK_OVERLAP = 10  # Words overlap between chunks
SCRAPED_TEXTS_PATH = Path("scraped_texts")  # Path to scraped texts
MODEL_NAME = "all-MiniLM-L6-v2"  # Lightweight and effective model

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks of specified size."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunk = " ".join(words[i:i+size])
        if chunk:
            chunks.append(chunk)
    return chunks

def get_embedding(text: str, model) -> np.ndarray:
    """Get embedding for text using Sentence Transformer model."""
    try:
        # The model.encode() method returns a numpy array
        return model.encode(text, convert_to_numpy=True).astype(np.float32)
    except Exception as e:
        print(f"Error getting embedding: {str(e)}")
        return None

def process_scraped_files(model):
    """Process all scraped text files and create FAISS index."""
    all_chunks = []
    metadata = []

    # Process each text file in the scraped_texts directory
    for file in SCRAPED_TEXTS_PATH.glob("*.txt"):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            
            # Extract URL from the content (first line after "URL: ")
            url = None
            for line in content.split('\n'):
                if line.startswith('URL: '):
                    url = line[5:].strip()
                    break
            
            if not url:
                continue  # Skip if URL not found
            
            # Get the actual content (skip the metadata lines)
            content_lines = content.split('\n\n', 1)
            if len(content_lines) > 1:
                actual_content = content_lines[1]
                
                # Create chunks
                chunks = chunk_text(actual_content)
                
                # Process each chunk
                for idx, chunk in enumerate(chunks):
                    embedding = get_embedding(chunk, model)
                    if embedding is not None:
                        all_chunks.append(embedding)
                        metadata.append({
                            "url": url,
                            "chunk": chunk,
                            "chunk_id": f"{file.stem}_{idx}"
                        })
        
        print(f"Processed: {file.name}")

    return all_chunks, metadata

def create_faiss_index(embeddings):
    """Create and return a FAISS index."""
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.stack(embeddings))
    return index

def search_history(query, model, index, metadata, k=3):
    """Search the history using the given query."""
    query_vec = get_embedding(query, model)
    if query_vec is None:
        return []
    
    query_vec = query_vec.reshape(1, -1)
    D, I = index.search(query_vec, k=k)
    
    results = []
    for idx in I[0]:
        results.append({
            "url": metadata[idx]["url"],
            "chunk": metadata[idx]["chunk"]
        })
    
    return results

def main():
    print(f"Loading Sentence Transformer model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    print("Model loaded successfully!")
    
    print("\nProcessing scraped history files...")
    embeddings, metadata = process_scraped_files(model)
    
    if not embeddings:
        print("No files found in scraped_texts directory!")
        return
    
    print(f"\n✅ Indexed {len(embeddings)} chunks from {len(list(SCRAPED_TEXTS_PATH.glob('*.txt')))} files")
    
    # Create FAISS index
    index = create_faiss_index(embeddings)
    
    # Interactive search loop
    while True:
        query = input("\n🔍 Enter your search query (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
            
        results = search_history(query, model, index, metadata)
        
        if not results:
            print("No results found or error occurred during search.")
            continue
            
        print("\n📚 Search Results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. URL: {result['url']}")
            print(f"   Content: {result['chunk']}")

if __name__ == "__main__":
    main() 
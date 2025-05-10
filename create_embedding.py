import os
from pathlib import Path
from memory import MemoryManager
from models import ChunkMetadata
import json
from logger_config import setup_logger

# Set up logger
logger = setup_logger("create_embedding")

def chunk_text(text: str, size: int = 50, overlap: int = 10) -> list:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunk = " ".join(words[i:i+size])
        if chunk:
            chunks.append(chunk)
    return chunks

def create_embeddings():
    """Create embeddings for all scraped texts and save them."""
    memory = MemoryManager()
    scraped_texts_path = Path("scraped_texts")
    embeddings_file = "embeddings.json"
    
    if not scraped_texts_path.exists():
        logger.error("scraped_texts directory not found!")
        return
    
    logger.info("Starting to process scraped history files...")
    total_chunks = 0
    
    for file in scraped_texts_path.glob("*.txt"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                
                # Extract URL
                url = None
                for line in content.split('\n'):
                    if line.startswith('URL: '):
                        url = line[5:].strip()
                        break
                
                if not url:
                    logger.warning(f"No URL found in file: {file.name}")
                    continue
                
                # Get actual content
                content_lines = content.split('\n\n', 1)
                if len(content_lines) > 1:
                    actual_content = content_lines[1]
                    
                    # Create chunks
                    chunks = chunk_text(actual_content)
                    file_chunks = 0
                    
                    # Process each chunk
                    for idx, chunk in enumerate(chunks):
                        metadata = ChunkMetadata(
                            url=url,
                            chunk=chunk,
                            chunk_id=f"{file.stem}_{idx}"
                        )
                        embedding = memory.get_embedding(chunk)
                        memory.add_chunk(metadata, embedding)
                        file_chunks += 1
                    
                    total_chunks += file_chunks
                    logger.info(f"Processed {file.name}: {file_chunks} chunks")
                else:
                    logger.warning(f"No content found in file: {file.name}")
        
        except Exception as e:
            logger.error(f"Error processing file {file.name}: {str(e)}")
    
    try:
        # Save embeddings and metadata
        embeddings_data = {
            "embeddings": [emb.tolist() for emb in memory.embeddings],
            "metadata": [meta.dict() for meta in memory.metadata]
        }
        
        with open(embeddings_file, 'w') as f:
            json.dump(embeddings_data, f)
        
        logger.info(f"Successfully created embeddings for {total_chunks} chunks")
        logger.info(f"Embeddings saved to: {embeddings_file}")
    
    except Exception as e:
        logger.error(f"Error saving embeddings: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting embedding creation process")
    create_embeddings()
    logger.info("Embedding creation process completed") 
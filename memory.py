import os
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Optional
from models import ChunkMetadata, SearchHistory
import json
from datetime import datetime
from logger_config import setup_logger

# Set up logger
logger = setup_logger("memory")

class MemoryManager:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"Initializing MemoryManager with model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.metadata: List[ChunkMetadata] = []
        self.embeddings: List[np.ndarray] = []
        self.search_history: List[SearchHistory] = []
        self.history_file = "search_history.json"
        self._load_history()

    def _load_history(self):
        """Load search history from file if it exists."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    history_data = json.load(f)
                    self.search_history = [
                        SearchHistory(**item) for item in history_data
                    ]
                logger.info(f"Loaded {len(self.search_history)} search history entries")
            except Exception as e:
                logger.error(f"Error loading history: {str(e)}")
        else:
            logger.info("No existing search history found")

    def _save_history(self):
        """Save search history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(
                    [history.dict() for history in self.search_history],
                    f,
                    default=str
                )
            logger.debug(f"Saved {len(self.search_history)} search history entries")
        except Exception as e:
            logger.error(f"Error saving history: {str(e)}")

    def add_to_history(self, query: str, num_results: int, result_urls: List[str]):
        """Add a search to history."""
        logger.info(f"Adding search to history: {query}")
        history_item = SearchHistory(
            query=query,
            timestamp=datetime.now(),
            num_results=num_results,
            result_urls=result_urls
        )
        self.search_history.append(history_item)
        self._save_history()

    def get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text using Sentence Transformer model."""
        logger.debug(f"Generating embedding for text of length {len(text)}")
        return self.model.encode(text, convert_to_numpy=True).astype(np.float32)

    def add_chunk(self, metadata: ChunkMetadata, embedding: np.ndarray):
        """Add a chunk and its embedding to the index."""
        logger.debug(f"Adding chunk {metadata.chunk_id} from {metadata.url}")
        self.metadata.append(metadata)
        self.embeddings.append(embedding)

        # Initialize or update index
        if self.index is None:
            logger.info("Initializing FAISS index")
            self.index = faiss.IndexFlatL2(len(embedding))
        self.index.add(np.stack([embedding]))

    def search(self, query: str, k: int = 3) -> List[tuple[ChunkMetadata, float]]:
        """Search for similar chunks."""
        if not self.index or len(self.metadata) == 0:
            logger.warning("No index available for search")
            return []

        logger.info(f"Searching for query: {query} with k={k}")
        query_vec = self.get_embedding(query).reshape(1, -1)
        D, I = self.index.search(query_vec, k)

        results = []
        for idx, distance in zip(I[0], D[0]):
            if idx < len(self.metadata):
                results.append((self.metadata[idx], float(distance)))
                logger.debug(f"Found match with distance {distance:.4f}")

        logger.info(f"Search completed with {len(results)} results")
        return results

    def get_recent_searches(self, limit: int = 5) -> List[SearchHistory]:
        """Get recent search history."""
        logger.info(f"Retrieving {limit} recent searches")
        return sorted(
            self.search_history,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit] 
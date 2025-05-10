from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChunkMetadata(BaseModel):
    url: str
    chunk: str
    chunk_id: str

class SearchResult(BaseModel):
    url: str
    content: str
    similarity_score: float

class SearchQuery(BaseModel):
    query_text: str
    timestamp: datetime = datetime.now()
    num_results: int = 3

class SearchHistory(BaseModel):
    query: str
    timestamp: datetime
    num_results: int
    result_urls: List[str]

class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: SearchQuery
    total_chunks_searched: int 
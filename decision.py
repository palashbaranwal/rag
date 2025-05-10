from typing import List, Tuple
from models import SearchQuery, SearchResult
from perception import SearchIntent
from memory import MemoryManager

def generate_search_plan(
    intent: SearchIntent,
    memory: MemoryManager
) -> Tuple[SearchQuery, bool]:
    """
    Generate search plan based on intent.
    Returns:
    - SearchQuery: The processed query with parameters
    - bool: Whether to show history instead of searching
    """
    if intent.is_history_request:
        return None, True
    
    return SearchQuery(
        query_text=intent.query,
        num_results=intent.num_results
    ), False

def process_search_results(
    results: List[Tuple[dict, float]],
    query: SearchQuery
) -> List[SearchResult]:
    """Process and format search results."""
    search_results = []
    for metadata, score in results:
        search_results.append(
            SearchResult(
                url=metadata.url,
                content=metadata.chunk,
                similarity_score=score
            )
        )
    return search_results 
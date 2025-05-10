from typing import List, Tuple
from models import SearchQuery, SearchResult
from perception import SearchIntent
from memory import MemoryManager
from logger_config import setup_logger

# Set up logger
logger = setup_logger("decision")

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
    logger.info(f"Generating search plan for intent: {intent.dict()}")
    
    if intent.is_history_request:
        logger.info("Intent is history request, will show history")
        return None, True
    
    search_query = SearchQuery(
        query_text=intent.query,
        num_results=intent.num_results
    )
    logger.info(f"Generated search query: {search_query.dict()}")
    return search_query, False

def process_search_results(
    results: List[Tuple[dict, float]],
    query: SearchQuery
) -> List[SearchResult]:
    """Process and format search results."""
    logger.info(f"Processing {len(results)} search results")
    search_results = []
    
    for metadata, score in results:
        search_results.append(
            SearchResult(
                url=metadata.url,
                content=metadata.chunk,
                similarity_score=score
            )
        )
        logger.debug(f"Processed result from {metadata.url} with score {score:.4f}")
    
    logger.info(f"Successfully processed {len(search_results)} results")
    return search_results 
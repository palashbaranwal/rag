from typing import List
from models import SearchQuery, SearchResult, SearchResponse
from memory import MemoryManager
from logger_config import setup_logger

# Set up logger
logger = setup_logger("action")

def execute_search(
    query: SearchQuery,
    memory: MemoryManager
) -> SearchResponse:
    """Execute the search and return formatted results."""
    logger.info(f"Executing search for query: {query.query_text}")
    
    # Perform the search
    results = memory.search(query.query_text, k=query.num_results)
    
    # Process results
    search_results = []
    result_urls = []
    
    for metadata, score in results:
        search_results.append(
            SearchResult(
                url=metadata.url,
                content=metadata.chunk,
                similarity_score=score
            )
        )
        result_urls.append(metadata.url)
        logger.debug(f"Added result from {metadata.url} with score {score:.4f}")
    
    # Add to search history
    memory.add_to_history(
        query=query.query_text,
        num_results=len(search_results),
        result_urls=result_urls
    )
    
    logger.info(f"Search completed with {len(search_results)} results")
    return SearchResponse(
        results=search_results,
        query=query,
        total_chunks_searched=len(memory.metadata)
    )

def show_search_history(memory: MemoryManager, limit: int = 5) -> List[dict]:
    """Show recent search history."""
    logger.info(f"Retrieving search history with limit {limit}")
    recent_searches = memory.get_recent_searches(limit)
    
    history_data = [
        {
            "query": search.query,
            "timestamp": search.timestamp,
            "num_results": search.num_results,
            "urls": search.result_urls
        }
        for search in recent_searches
    ]
    
    logger.info(f"Retrieved {len(history_data)} history entries")
    return history_data 
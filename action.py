from typing import List
from models import SearchQuery, SearchResult, SearchResponse
from memory import MemoryManager

def execute_search(
    query: SearchQuery,
    memory: MemoryManager
) -> SearchResponse:
    """Execute the search and return formatted results."""
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
    
    # Add to search history
    memory.add_to_history(
        query=query.query_text,
        num_results=len(search_results),
        result_urls=result_urls
    )
    
    return SearchResponse(
        results=search_results,
        query=query,
        total_chunks_searched=len(memory.metadata)
    )

def show_search_history(memory: MemoryManager, limit: int = 5) -> List[dict]:
    """Show recent search history."""
    recent_searches = memory.get_recent_searches(limit)
    return [
        {
            "query": search.query,
            "timestamp": search.timestamp,
            "num_results": search.num_results,
            "urls": search.result_urls
        }
        for search in recent_searches
    ] 
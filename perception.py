from pydantic import BaseModel
from typing import Optional

class SearchIntent(BaseModel):
    query: str
    is_history_request: bool = False
    num_results: int = 3

def extract_perception(query: str) -> SearchIntent:
    """
    Extract search intent from user query.
    Currently handles:
    - Regular search queries
    - History requests (if query contains 'history' or 'recent')
    """
    query = query.lower().strip()
    
    # Check if it's a history request
    is_history_request = any(word in query for word in ['history', 'recent', 'previous'])
    
    # Default to 3 results unless specified
    num_results = 3
    
    return SearchIntent(
        query=query,
        is_history_request=is_history_request,
        num_results=num_results
    ) 
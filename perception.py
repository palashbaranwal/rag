from pydantic import BaseModel
from typing import Optional
from logger_config import setup_logger

# Set up logger
logger = setup_logger("perception")

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
    logger.info(f"Extracting intent from query: {query}")
    query = query.lower().strip()
    
    # Check if it's a history request
    is_history_request = any(word in query for word in ['history', 'recent', 'previous'])
    
    # Default to 3 results unless specified
    num_results = 3
    
    intent = SearchIntent(
        query=query,
        is_history_request=is_history_request,
        num_results=num_results
    )
    
    logger.info(f"Extracted intent: {intent.dict()}")
    return intent 
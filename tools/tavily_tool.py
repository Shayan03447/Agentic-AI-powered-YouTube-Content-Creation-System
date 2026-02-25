import os
import logging
from typing import Optional, Any
from tavily import TavilyClient
from dotenv import load_dotenv
load_dotenv()

logger=logging.getLogger(__name__)
_client: Optional[TavilyClient]=None

def _get_client()-> TavilyClient:
    """Create or return the shared Tavily client. Fails if API key is missing"""
    global _client
    if _client is not None:
        return _client
    api_key=os.environ.get("TAVILY_API_KEY")
    if not api_key or not str(api_key).strip():
        raise ValueError("TAVILY_API_KEY is not set or empty in environment")
    _client=TavilyClient(api_key=api_key.strip())
    return _client    

def tavily_search(
    query: str,
    max_results: Optional[int] = 5,
    search_depth: str = "basic",
    include_answer: bool = False,
    topic: str = "general",
) -> dict[str, Any]:
    """Run the Tavily web search with full error handling"""
    if query is None or not str(query).strip():
        return {"results": [], "answer": None, "error": "Search query cannot be empty"}
    query = str(query).strip()

    if max_results is not None:
        if not isinstance(max_results, int) or max_results < 1 or max_results > 20:
            return {"results": [], "answer": None, "error": "max_results must be an integer between 1 and 20"}
    else:
        max_results=5

    if search_depth not in ("basic", "advanced"):
        return {"results":[], "answer": None, "error": "search_depth must be 'basic' or 'advanced'"}

    if  topic not in ("general", "news"):
        return {"results": [], "answer": None, "error": "topic must be 'general' or 'news'"}
    
    try:
        client=_get_client()
    except ValueError as e:
        logger.error(f"Failed to get Tavily client: %s", e)
        return {"results": [], "answer": None, "error": str(e)}

    try:
        response= client.search(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            include_answer=include_answer,
            topic=topic,
        )
    except Exception as e:
        logger.exception("Tavily search failed for query=%r : %s", query, e)
        return {"results": [], "answer": None, "error":f"Search failed: {e}"}

    if isinstance(response, dict):
        results=response.get("results")
        answer=response.get("answer") if include_answer else None
    else:
        results=getattr(response, "results", None)
        answer=getattr(response, "answer", None) if include_answer else None

    if results is None:
        results=[]
    if not isinstance(results, list):
        results = []
    return {"results": results, "answer":answer, "error": None}

if __name__ == "__main__":
    client = _get_client()
    result = client.search("Python programming")
    print(result)

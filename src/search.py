import os
from tavily import TavilyClient
from pydantic import BaseModel
from dotenv import load_dotenv
import logging

# Load secrets
load_dotenv()

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tavily_search")

# Initialize Client
tavily_api_key = os.getenv("TAVILY_API_KEY")

class SearchResult(BaseModel):
    url: str
    title: str
    content: str

def perform_search(query: str, max_results: int = 3) -> list[dict]:
    """
    Searches the web and returns clean text content.
    Returns a list of dictionaries.
    """
    if not tavily_api_key:
        logger.error("Attempted search without API key.")
        return []

    client = TavilyClient(api_key=tavily_api_key)
    
    try:
        logger.info(f"🔍 Searching for: {query}")
        response = client.search(
            query=query, 
            search_depth="advanced", 
            max_results=max_results,
            include_raw_content=False
        )
        
        results = []
        for result in response.get("results", []):
            results.append({
                "url": result["url"],
                "title": result["title"],
                "content": result["content"][:2000]
            })
        
        logger.info(f"✅ Found {len(results)} results.")
        return results
        
    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        return []
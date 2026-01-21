from mcp.server.fastmcp import FastMCP
from src.schema import KnowledgeGraphUpdate
from src.search import perform_search
from src.graph_ops import insert_knowledge
import logging

# Initialize Logging
logging.basicConfig(level=logging.INFO)
mcp = FastMCP("Gotham Knowledge Graph")

@mcp.tool()
def add_knowledge(data: KnowledgeGraphUpdate) -> str:
    """
    Ingests extracted knowledge into the Neo4j Graph.
    Idempotently merges Nodes and Relationships.
    """
    # Delegate to the core logic in graph_ops
    return insert_knowledge(data)

@mcp.tool()
def search_web(query: str) -> str:
    """
    Searches the web for information using Tavily.
    Returns the top 3 results formatted as a string.
    """
    # Delegate to the core logic in search module
    results = perform_search(query)
    
    formatted_output = f"--- Search Results for '{query}' ---\n"
    for r in results:
        formatted_output += f"Source: {r['title']} ({r['url']})\n"
        formatted_output += f"Content: {r['content']}\n"
        formatted_output += "-" * 20 + "\n"
        
    return formatted_output

if __name__ == "__main__":
    mcp.run()
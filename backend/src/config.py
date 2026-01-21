import os
from dotenv import load_dotenv

# Load env vars once here
load_dotenv()

class Config:
    # Model Configuration
    LLM_PROVIDER = "google" # or "openai"
    MODEL_NAME = os.getenv("LLM_MODEL", "gemini-2.5-flash") # Default to Flash
    
    # Search Configuration
    MAX_SEARCH_RESULTS = 3
    
    # Neo4j Configuration
    NEO4J_URI = os.getenv("NEO4J_URI", f"bolt://localhost:{os.getenv('NEO4J_BOLT_PORT', 7687)}")
    NEO4J_USER = os.getenv("NEO4J_AUTH", "").split("/")[0]
    NEO4J_PASSWORD = os.getenv("NEO4J_AUTH", "").split("/")[1]

    @staticmethod
    def validate():
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("Missing GOOGLE_API_KEY in .env")
        if not os.getenv("TAVILY_API_KEY"):
            raise ValueError("Missing TAVILY_API_KEY in .env")
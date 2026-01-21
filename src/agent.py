from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from src.config import Config
from src.search import perform_search
from src.graph_ops import insert_knowledge
from src.schema import KnowledgeGraphUpdate
import logging

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gotham_agent")

# 1. Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model=Config.MODEL_NAME,
    temperature=0,
    convert_system_message_to_human=True
)

# 2. Define Tools
@tool
def search_tavily(query: str):
    """
    Search the web for information using Tavily.
    Use this to gather facts before saving them to the database.
    """
    return perform_search(query, max_results=Config.MAX_SEARCH_RESULTS)

@tool
def save_to_graph(data: KnowledgeGraphUpdate):
    """
    Save extracted entities and relationships to the Knowledge Graph.
    Use this AFTER gathering information.
    Input must be a valid JSON object matching the KnowledgeGraphUpdate schema.
    """
    if isinstance(data, dict):
        data = KnowledgeGraphUpdate(**data)
    return insert_knowledge(data)

# 3. Create the Agent
tools = [search_tavily, save_to_graph]
agent_executor = create_react_agent(llm, tools)

def run_agent(user_input: str):
    """
    Entry point to run the agent.
    """
    logger.info(f"🤖 Agent Task: {user_input}")
    
    # Run the graph
    for step in agent_executor.stream(
        {"messages": [("user", user_input)]},
        stream_mode="values"
    ):
        last_msg = step["messages"][-1]
        print(f"\n--- {last_msg.type.upper()} ---")
        
        # We restore the simple print logic that worked for you
        if last_msg.content:
            print(last_msg.content)
            
        # Optional: Keep the 'tool check' just in case, but it's not required if the base works
        if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
             print(f"🛠️  AGENT WANTS TO CALL: {last_msg.tool_calls[0]['name']}")
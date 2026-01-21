from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.agent import agent_executor
import logging

# Initialize API
app = FastAPI(title="Gotham OSINT API", version="1.0")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

# Define the Request Body
class MissionRequest(BaseModel):
    task: str

@app.get("/")
def health_check():
    """
    Simple heartbeat endpoint to see if server is running.
    """
    return {"status": "operational", "system": "Project Gotham"}

@app.post("/run-mission")
async def run_mission(request: MissionRequest):
    """
    Endpoint to trigger the Autonomous Agent.
    Next.js will send a POST request here with the user's prompt.
    """
    task = request.task
    logger.info(f"🚀 Received Mission: {task}")
    
    try:
        # We run the agent and capture the final state
        # invoke() runs the whole chain and returns the final result
        result = agent_executor.invoke({"messages": [("user", task)]})
        
        # Extract the last message from the AI to send back to UI
        last_message = result["messages"][-1].content
        
        return {
            "mission": task,
            "result": last_message,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Mission Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
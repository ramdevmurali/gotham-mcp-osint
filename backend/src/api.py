import logging
import uuid

from fastapi import FastAPI, HTTPException
import asyncio
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from src.agent import run_agent
from src.config import Config
from src.graph_db import GraphManager

app = FastAPI(title="Gotham OSINT API", version="1.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

class MissionRequest(BaseModel):
    task: str
    thread_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

@app.get("/")
def health():
    return {"status": "operational"}


@app.get("/graph/sample")
async def graph_sample(doc_limit: int = 5):
    """
    Return a lightweight sample of the graph for the frontend preview.
    - Pulls latest documents (by created_at) up to doc_limit
    - Returns distinct nodes/edges plus counts
    """
    db = GraphManager()

    def query():
        cypher = """
        MATCH (d:Document)
        WITH d ORDER BY coalesce(d.created_at, 0) DESC LIMIT $doc_limit
        OPTIONAL MATCH (d)-[:MENTIONS]->(e)
        OPTIONAL MATCH (e)-[r:RELATED]->(t)
        WITH collect(distinct d) AS docs, collect(distinct e) AS ent_nodes, collect(distinct t) AS target_nodes, collect(distinct r) AS rels
        WITH docs,
             [n IN ent_nodes + target_nodes WHERE n IS NOT NULL | {id: elementId(n), labels: labels(n), name: coalesce(n.name, n.url), props: properties(n)}] AS nodes,
             [r IN rels WHERE r IS NOT NULL | {id: elementId(r), type: type(r), source: elementId(startNode(r)), target: elementId(endNode(r)), props: properties(r)}] AS edges
        RETURN nodes,
               edges,
               size(nodes) AS node_count,
               size(edges) AS edge_count,
               [d IN docs | {id: elementId(d), url: d.url, created_at: d.created_at}] AS documents
        """
        with db.session() as session:
            record = session.run(cypher, {"doc_limit": doc_limit}).single()
            if not record:
                return {
                    "nodes": [],
                    "edges": [],
                    "node_count": 0,
                    "edge_count": 0,
                    "documents": [],
                }
            return {
                "nodes": record["nodes"],
                "edges": record["edges"],
                "node_count": record["node_count"],
                "edge_count": record["edge_count"],
                "documents": record["documents"],
            }

    try:
        data = await asyncio.wait_for(run_in_threadpool(query), timeout=10)
        return data
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Graph sample timed out")
    except Exception as e:
        logger.error(f"Graph sample error: {e}")
        raise HTTPException(status_code=500, detail="Graph sample failed")


@app.get("/graph/stats")
async def graph_stats():
    """
    Return aggregate stats for the graph (entities, sources, dedupe confidence).
    """
    db = GraphManager()

    def query():
        cypher = """
        MATCH (n)
        WHERE any(l IN labels(n) WHERE l IN ["Person","Organization","Location","Topic"])
        WITH count(n) AS entity_count, count(distinct toLower(trim(n.name))) AS distinct_names
        MATCH (d:Document)
        RETURN entity_count AS entities,
               count(d)    AS sources,
               (CASE
                    WHEN entity_count = 0 THEN 100
                    ELSE round(100.0 * distinct_names / entity_count)
               END) AS dedupe_confidence
        """
        with db.session() as session:
            record = session.run(cypher).single()
            if not record:
                return {"entities": 0, "sources": 0, "dedupe_confidence": 100}
            return {
                "entities": record["entities"],
                "sources": record["sources"],
                "dedupe_confidence": record["dedupe_confidence"],
            }

    try:
        data = await asyncio.wait_for(run_in_threadpool(query), timeout=8)
        return data
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Graph stats timed out")
    except Exception as e:
        logger.error(f"Graph stats error: {e}")
        raise HTTPException(status_code=500, detail="Graph stats failed")

@app.post("/run-mission")
async def run_mission(req: MissionRequest):
    logger.info(f"Task: {req.task} | Thread: {req.thread_id}")
    
    try:
        content = await asyncio.wait_for(
            run_in_threadpool(run_agent, req.task, req.thread_id),
            timeout=Config.RUN_MISSION_TIMEOUT,
        )

        return {
            "result": content,
            "thread_id": req.thread_id,
            "status": "success"
        }
        
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Mission timed out")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

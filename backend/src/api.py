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

class CompanyRequest(BaseModel):
    company: str
    thread_id: str | None = None

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


@app.post("/agents/profile-company")
async def profile_company(req: CompanyRequest):
    """
    Company profiler: builds a concise profile and writes to the graph.
    """
    if not req.company:
        raise HTTPException(status_code=400, detail="company is required")

    task = (
        f"Profile the company '{req.company}'. "
        "Return canonical name, HQ/country, founded year, and 3 key executives with roles. "
        "Cite at least 3 recent sources (title + URL) and save entities/relationships to the graph."
    )

    try:
        content = await asyncio.wait_for(
            run_in_threadpool(run_agent, task, req.thread_id or str(uuid.uuid4())),
            timeout=Config.RUN_MISSION_TIMEOUT,
        )
        return {"result": content, "status": "success"}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Profiler timed out")
    except Exception as e:
        logger.error(f"Profiler error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/competitors")
async def competitor_scout(req: CompanyRequest):
    """
    Competitor scout: finds 3-5 close competitors and writes COMPETES_WITH edges.
    """
    if not req.company:
        raise HTTPException(status_code=400, detail="company is required")

    task = (
        f"Find 3-5 close competitors for '{req.company}'. "
        "For each competitor, give a one-line rationale and at least one source URL. "
        "Create Organization nodes if needed and write COMPETES_WITH relationships from the target company "
        "to each competitor, setting relationship properties reason and source_url. "
        "Use save_to_graph with entities [{name: <company>, label: 'Organization'}, {name: <competitor>, label: 'Organization'}] "
        "and relationships [{source: <company>, target: <competitor>, type: 'COMPETES_WITH', properties: {reason: <why>, source_url: <url>}}]. "
        "Pick competitors from credible recent sources."
    )

    try:
        content = await asyncio.wait_for(
            run_in_threadpool(run_agent, task, req.thread_id or str(uuid.uuid4())),
            timeout=Config.RUN_MISSION_TIMEOUT,
        )
        # After run, fetch competitors from graph for convenience
        competitors = await get_competitors(req.company)
        return {"result": content, "status": "success", "competitors": competitors["competitors"]}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Competitor scout timed out")
    except Exception as e:
        logger.error(f"Competitor scout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/graph/competitors")
async def get_competitors(company: str):
    """Return competitors for a given company from the graph."""
    if not company:
        raise HTTPException(status_code=400, detail="company is required")
    db = GraphManager()

    def query():
        cypher = """
        MATCH (c:Organization)
        WHERE toLower(c.name) = toLower($company)
        MATCH (c)-[r:RELATED {type:'COMPETES_WITH'}]->(o:Organization)
        RETURN o.name AS competitor, r.reason AS reason, r.source_url AS source
        ORDER BY o.name
        """
        with db.session() as session:
            return [
                {"competitor": rec["competitor"], "reason": rec["reason"], "source": rec["source"]}
                for rec in session.run(cypher, {"company": company})
            ]

    try:
        data = await asyncio.wait_for(run_in_threadpool(query), timeout=8)
        return {"company": company, "competitors": data}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Competitors query timed out")
    except Exception as e:
        logger.error(f"Competitors query error: {e}")
        raise HTTPException(status_code=500, detail="Competitors query failed")


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

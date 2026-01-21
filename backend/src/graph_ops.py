import logging
from src.graph_db import GraphManager
from src.schema import KnowledgeGraphUpdate

# Configure logger locally so we see what's happening
logger = logging.getLogger("graph_ops")

def insert_knowledge(data: KnowledgeGraphUpdate) -> str:
    """
    Pure Python function to ingest knowledge.
    Separated from the Server/API layer.
    """
    # 1. Initialize Connection (Singleton)
    db = GraphManager()
    
    logger.info(f"Writing to Graph for Source: {data.source_url}")

    # 2. Create Document Node
    query_doc = """
    MERGE (d:Document {url: $url})
    ON CREATE SET d.created_at = timestamp()
    """
    with db.driver.session() as session:
        session.run(query_doc, url=data.source_url)

    # 3. Process Entities
    count_entities = 0
    with db.driver.session() as session:
        for entity in data.entities:
            # Safe Cypher injection using parameters
            cypher = f"""
            MERGE (e:{entity.label} {{name: $name}})
            ON CREATE SET e += $props
            ON MATCH SET e += $props
            """
            session.run(cypher, name=entity.name, props=entity.properties)
            count_entities += 1

    # 4. Process Relationships
    count_rels = 0
    with db.driver.session() as session:
        for rel in data.relationships:
            cypher = f"""
            MATCH (source {{name: $source_name}})
            MATCH (target {{name: $target_name}})
            MATCH (doc:Document {{url: $doc_url}})
            
            // Create the semantic relationship
            MERGE (source)-[r:{rel.type}]->(target)
            ON CREATE SET r += $props
            
            // Create provenance edges (Source -> Doc)
            MERGE (doc)-[:MENTIONS]->(source)
            MERGE (doc)-[:MENTIONS]->(target)
            """
            try:
                session.run(cypher, 
                            source_name=rel.source, 
                            target_name=rel.target, 
                            doc_url=data.source_url,
                            props=rel.properties)
                count_rels += 1
            except Exception as e:
                logger.error(f"Failed to link {rel.source} -> {rel.target}: {e}")

    result_msg = f"Successfully ingested {count_entities} entities and {count_rels} relationships from {data.source_url}"
    logger.info(result_msg)
    return result_msg
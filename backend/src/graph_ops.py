import logging
from src.graph_db import GraphManager
from src.schema import KnowledgeGraphUpdate

logger = logging.getLogger("graph_ops")

def resolve_entity(session, name, label):
    """
    Automatic Entity Resolution.
    Returns the EXISTING name if found, otherwise returns the NEW name.
    """
    # 1. Exact Match Check (Fastest)
    exact_query = f"MATCH (n:{label}) WHERE n.name = $name RETURN n.name LIMIT 1"
    result = session.run(exact_query, name=name).single()
    if result:
        return result[0]

    # 2. Fuzzy Match Check (Slower but smarter)
    # We ask Neo4j: "Find names similar to this one" (~ means fuzzy)
    # Score > 0.6 means "At least 60% similar"
    fuzzy_query = f"""
    CALL db.index.fulltext.queryNodes("entity_name_index", $name + "~") YIELD node, score
    WHERE labels(node)[0] = $label AND score > 0.6
    RETURN node.name, score ORDER BY score DESC LIMIT 1
    """
    try:
        result = session.run(fuzzy_query, name=name, label=label).single()
        if result:
            existing_name = result['node.name']
            score = result['score']
            logger.info(f"🔄 RESOLUTION: Merging '{name}' -> Existing '{existing_name}' (Score: {score:.2f})")
            return existing_name
    except Exception as e:
        logger.warning(f"Fuzzy search skipped (Index missing?): {e}")
    
    return name

def insert_knowledge(data: KnowledgeGraphUpdate) -> str:
    db = GraphManager()
    logger.info(f"Writing to Graph for Source: {data.source_url}")

    with db.driver.session() as session:
        # 1. Create Document Node
        session.run("""
        MERGE (d:Document {url: $url})
        ON CREATE SET d.created_at = timestamp()
        """, url=data.source_url)

        # 2. Process Entities with RESOLUTION
        name_map = {} 
        
        for entity in data.entities:
            # Smart Resolve the name
            final_name = resolve_entity(session, entity.name, entity.label)
            name_map[entity.name] = final_name # Keep track: "Space-X" is actually "SpaceX"
            
            cypher = f"""
            MERGE (e:{entity.label} {{name: $name}})
            ON CREATE SET e += $props
            ON MATCH SET e += $props
            """
            session.run(cypher, name=final_name, props=entity.properties)

        # 3. Process Relationships using RESOLVED names
        count_rels = 0
        for rel in data.relationships:
            # If we resolved "Space-X" to "SpaceX", we must use "SpaceX" here
            source_final = name_map.get(rel.source, rel.source)
            target_final = name_map.get(rel.target, rel.target)
            
            cypher = f"""
            MATCH (source {{name: $source_name}})
            MATCH (target {{name: $target_name}})
            MATCH (doc:Document {{url: $doc_url}})
            
            MERGE (source)-[r:{rel.type}]->(target)
            ON CREATE SET r += $props
            
            MERGE (doc)-[:MENTIONS]->(source)
            MERGE (doc)-[:MENTIONS]->(target)
            """
            try:
                session.run(cypher, 
                            source_name=source_final, 
                            target_name=target_final, 
                            doc_url=data.source_url,
                            props=rel.properties)
                count_rels += 1
            except Exception as e:
                logger.error(f"Failed to link {source_final} -> {target_final}: {e}")

    return f"Successfully ingested {len(data.entities)} entities and {count_rels} relationships from {data.source_url}"

# We keep this for the agent tool, but it essentially points to the same logic
def lookup_entity(name: str) -> str:
    db = GraphManager()
    with db.driver.session() as session:
        # We can reuse the smart logic here to tell the agent what we found
        # (This is just a helper for the agent's 'check_graph' tool)
        label = "Organization" # Default assumption for checking
        found = resolve_entity(session, name, label)
        if found != name:
            return f"Found existing entity: {found}"
        return "No exact match found."
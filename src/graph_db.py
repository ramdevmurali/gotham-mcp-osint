import os
import logging
from neo4j import GraphDatabase, Driver
from dotenv import load_dotenv

# Load secrets immediately
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphManager:
    """
    Singleton class to manage Neo4j connections and Schema constraints.
    Ensures we don't leak connections or create duplicate entities.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GraphManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        uri = f"bolt://localhost:{os.getenv('NEO4J_BOLT_PORT', 7687)}"
        user = os.getenv("NEO4J_AUTH", "").split("/")[0]
        password = os.getenv("NEO4J_AUTH", "").split("/")[1]
        
        try:
            self.driver: Driver = GraphDatabase.driver(uri, auth=(user, password))
            self.verify_connectivity()
            logger.info("✅ Neo4j Connection Established.")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            raise e

    def verify_connectivity(self):
        self.driver.verify_connectivity()

    def close(self):
        if self.driver:
            self.driver.close()
            logger.info("Neo4j Connection Closed.")

    def setup_constraints(self):
        """
        Idempotency is Law. 
        We define constraints here to prevent duplicate nodes at the database level.
        """
        queries = [
            # 1. Document Uniqueness (URL is the source of truth)
            "CREATE CONSTRAINT document_url_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.url IS UNIQUE",
            
            # 2. Entity Uniqueness (Resolving by Name for now)
            "CREATE CONSTRAINT person_name_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE",
            "CREATE CONSTRAINT org_name_unique IF NOT EXISTS FOR (o:Organization) REQUIRE o.name IS UNIQUE",
            "CREATE CONSTRAINT loc_name_unique IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE",
            "CREATE CONSTRAINT topic_name_unique IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE",
            
            # 3. Performance Indices (Faster lookups)
            "CREATE INDEX person_name_index IF NOT EXISTS FOR (p:Person) ON (p.name)",
        ]
        
        with self.driver.session() as session:
            for q in queries:
                try:
                    session.run(q)
                    logger.info(f"Executed Constraint: {q.split('REQUIRE')[1].strip()}")
                except Exception as e:
                    logger.error(f"Failed to execute {q}: {e}")

if __name__ == "__main__":
    # When run directly, initialize DB and apply schema
    db = GraphManager()
    db.setup_constraints()
    db.close()
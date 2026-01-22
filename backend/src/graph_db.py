import logging
from neo4j import GraphDatabase, Driver
from dotenv import load_dotenv
from src.config import Config

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GraphManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        uri = Config.NEO4J_URI
        user = Config.NEO4J_USER
        password = Config.NEO4J_PASSWORD
        
        try:
            self.driver: Driver = GraphDatabase.driver(uri, auth=(user, password))
            self.verify_connectivity()
            logger.info(f"✅ Connected to Neo4j: {uri}")
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
        queries = [
            "CREATE CONSTRAINT document_url_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.url IS UNIQUE",
            "CREATE CONSTRAINT person_name_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE",
            "CREATE CONSTRAINT org_name_unique IF NOT EXISTS FOR (o:Organization) REQUIRE o.name IS UNIQUE",
            
            # --- CRITICAL FOR FUZZY MATCHING ---
            "CREATE FULLTEXT INDEX entity_name_index IF NOT EXISTS FOR (n:Person|Organization) ON EACH [n.name]",
        ]
        
        with self.driver.session() as session:
            for q in queries:
                try:
                    session.run(q)
                    logger.info(f"Executed Constraint: {q}")
                except Exception as e:
                    logger.error(f"Failed to execute {q}: {e}")

if __name__ == "__main__":
    db = GraphManager()
    db.setup_constraints()
    db.close()
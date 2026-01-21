import logging
from neo4j import GraphDatabase, Driver
from dotenv import load_dotenv
from src.config import Config

# Load secrets immediately
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphManager:
    """
    Singleton class to manage Neo4j connections.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            # Standard Singleton implementation
            cls._instance = super(GraphManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # We read all connection parameters directly from the Config
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
        """
        Apply Schema Constraints to ensure Data Integrity.
        """
        queries = [
            "CREATE CONSTRAINT document_url_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.url IS UNIQUE",
            "CREATE CONSTRAINT person_name_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE",
            "CREATE CONSTRAINT org_name_unique IF NOT EXISTS FOR (o:Organization) REQUIRE o.name IS UNIQUE",
            "CREATE CONSTRAINT loc_name_unique IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE",
            "CREATE CONSTRAINT topic_name_unique IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE",
        ]
        
        with self.driver.session() as session:
            for q in queries:
                try:
                    session.run(q)
                    # Simple logging for success
                    logger.info(f"Executed Constraint: {q}")
                except Exception as e:
                    logger.error(f"Failed to execute {q}: {e}")

if __name__ == "__main__":
    # When run directly, initialize DB and apply schema
    db = GraphManager()
    db.setup_constraints()
    db.close()
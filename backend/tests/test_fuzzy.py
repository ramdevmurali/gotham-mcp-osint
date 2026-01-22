import logging
from src.graph_ops import insert_knowledge
from src.schema import KnowledgeGraphUpdate, Entity

# Setup logging to see the "Resolution" message
logging.basicConfig(level=logging.INFO)

print("🧪 TESTING FUZZY MATCHING...")

# 1. Create Data with a deliberate "Typo/Variation"
# We assume "SpaceX" is already in the DB. 
# We will try to save "Space-X" (Hyphenated).
mock_data = KnowledgeGraphUpdate(
    source_url="https://fuzzy-test.com",
    entities=[
        Entity(
            name="Space-X",  # <--- VARIATION
            label="Organization", 
            properties={"note": "This should be merged into SpaceX automatically"}
        )
    ],
    relationships=[]
)

# 2. Run the Ingestion
# If logic works, it should detect "SpaceX" exists and rewrite this to "SpaceX"
insert_knowledge(mock_data)

print("\n------------------------------------------------")
print("❓ DID IT WORK?")
print("Look for a log above saying: '🔄 RESOLUTION: Merging...'")
print("------------------------------------------------")
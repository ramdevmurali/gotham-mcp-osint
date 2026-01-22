import pytest

from src.schema import KnowledgeGraphUpdate, Entity, Relationship
from src.server import add_knowledge

@pytest.mark.integration
def test_ingest_mock_data():
    mock_data = KnowledgeGraphUpdate(
        source_url="https://project-gotham.test/briefing-001",
        entities=[
            Entity(name="Sarah Connor", label="Person", properties={"role": "Target", "status": "Active"}),
            Entity(name="Cyberdyne Systems", label="Organization", properties={"industry": "Defense"}),
            Entity(name="Los Angeles", label="Location", properties={})
        ],
        relationships=[
            Relationship(source="Sarah Connor", target="Cyberdyne Systems", type="INVESTIGATING", properties={"method": "physical_surveillance"}),
            Relationship(source="Cyberdyne Systems", target="Los Angeles", type="LOCATED_IN", properties={})
        ]
    )

    result = add_knowledge(mock_data)
    assert "Ingested" in result

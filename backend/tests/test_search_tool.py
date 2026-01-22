import pytest

from src.server import search_web

@pytest.mark.integration
def test_search_web():
    result = search_web("What is the capital of Montenegro?")
    assert "Search Results" in result

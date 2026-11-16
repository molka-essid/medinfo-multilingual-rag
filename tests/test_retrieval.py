import os
import pytest
from app.retrieve import retrieve

@pytest.mark.skipif(not os.path.exists(os.getenv("CHROMA_DIR", "./data/chroma")), reason="no index")
def test_retrieve_returns_results():
    res = retrieve("What is diabetes?", k=3)
    assert len(res) == 3
    assert all("text" in r for r in res)

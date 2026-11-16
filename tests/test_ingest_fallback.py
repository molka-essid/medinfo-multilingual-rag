import os
import httpx
import pytest
from unittest.mock import patch, MagicMock
from app import ingest


def test_date_fallback(monkeypatch, tmp_path):
    monkeypatch.setenv("MEDLINEPLUS_XML_URL", "")
    monkeypatch.setenv("RAW_DIR", str(tmp_path))
    monkeypatch.setattr(ingest, "RAW_DIR", str(tmp_path))
    calls = {"n": 0}

    def fake_get(url, timeout=120, follow_redirects=True):
        calls["n"] += 1
        resp = MagicMock()
        if calls["n"] < 3:
            resp.raise_for_status.side_effect = httpx.HTTPError("404")
            return resp
        resp.raise_for_status.return_value = None
        resp.text = "<health-topics></health-topics>"
        return resp

    with patch("app.ingest.httpx.get", side_effect=fake_get):
        path, fname = ingest.download(refresh=True)
    assert calls["n"] == 3
    assert os.path.exists(path)

import json
import os
import sys
from tempfile import TemporaryDirectory

# Ensure src/ imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from outputs.exporters import export_data  # type: ignore
from outputs.schema import Follower, normalize_record_list  # type: ignore

def test_export_and_roundtrip_json_csv():
    raw = [
        {
            "id": "1001",
            "name": "Alice Example",
            "url": "https://facebook.com/alice.example",
            "gender": "FEMALE",
            "friendship_status": "CAN_REQUEST",
            "subtitle_text": "Paris, France",
            "image": "https://cdn.example.com/alice.jpg",
        },
        {
            "id": "1002",
            "name": "Bob Sample",
            "url": "http://m.facebook.com/bob.sample",
            "gender": None,
            "friendship_status": "UNKNOWN",
            "subtitle_text": None,
            "image": None,
        },
    ]
    models = normalize_record_list(raw)
    assert len(models) == 2
    assert isinstance(models[0], Follower)
    assert models[1].url == "https://www.facebook.com/bob.sample"

    with TemporaryDirectory() as tmp:
        files = export_data(models, outdir=tmp, base_name="followers_test", formats=["json", "csv"])
        assert any(f.endswith(".json") for f in files)
        assert any(f.endswith(".csv") for f in files)

        json_path = [f for f in files if f.endswith(".json")][0]
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list) and len(data) == 2
        assert data[0]["name"] == "Alice Example"
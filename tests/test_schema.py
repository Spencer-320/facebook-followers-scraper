import os
import sys

# Ensure src/ imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from outputs.schema import Follower  # type: ignore

def test_normalizes_url_and_short_name():
    raw = {
        "id": " 123 ",
        "url": "facebook.com/john.doe.123?ref=bookmarks",
        "name": "John Doe",
        "gender": "male",
        "friendship_status": "following",
        "image": "https://example.com/p.jpg",
        "subtitle_text": " New York ",
    }
    model = Follower.model_validate(raw)
    assert model.url == "https://www.facebook.com/john.doe.123"
    assert model.short_name == "John"
    assert model.gender is None  # 'male' -> normalized to None (unsupported -> None)
    assert model.friendship_status == "FOLLOWING"
    assert model.title == "John Doe"
    assert model.subtitle_text == "New York"
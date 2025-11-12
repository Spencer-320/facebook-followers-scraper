import logging
import random
from typing import Any, Dict, List, Optional

from .dom_utils import clean_text, human_delay_ms, normalize_fb_url

class FacebookFollowersExtractor:
    """
    Demo extractor that simulates scrolling & extraction.
    In a real environment this would drive a headless browser and parse the DOM.

    Behavior:
      - If seed_followers is provided, it truncates to max_items and returns them after cleaning.
      - Otherwise, it generates deterministic sample followers for demonstration.
    """

    def __init__(self, scroll_delay_ms: int = 600, min_wait_ms: int = 300, max_wait_ms: int = 900):
        self.scroll_delay_ms = scroll_delay_ms
        self.min_wait_ms = min_wait_ms
        self.max_wait_ms = max_wait_ms

    def _fabricate_sample(self, max_items: int) -> List[Dict[str, Any]]:
        # Deterministic pseudo-random for repeatable runs
        random.seed(42)
        samples: List[Dict[str, Any]] = []
        base_users = [
            {
                "id": "100048901720805",
                "image": "https://example-cdn.fbcdn.net/profile1.jpg",
                "title": "Janet Alabi",
                "subtitle_text": "Lancaster, Pennsylvania",
                "url": "facebook.com/janet.alabi.37819",
                "friendship_status": "CAN_REQUEST",
                "gender": "FEMALE",
                "name": "Janet Alabi",
            },
            {
                "id": "100093221100654",
                "image": "https://example-cdn.fbcdn.net/profile2.jpg",
                "title": "Louis Park",
                "subtitle_text": "Berlin, Germany",
                "url": "http://facebook.com/louis.park.522",
                "friendship_status": "UNKNOWN",
                "gender": None,
                "name": "Louis Park",
            },
        ]
        # Clone and synthesize up to max_items
        while len(samples) < max_items:
            template = random.choice(base_users).copy()
            # Slightly vary ids and names
            template["id"] = str(int(template["id"]) + len(samples) + 1)
            if "name" in template:
                template["title"] = template["name"]
            samples.append(template)
        return samples[:max_items]

    def run(
        self, url: str, max_items: int = 50, seed_followers: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        logging.debug("Starting simulated scroll on URL='%s'", url)
        total_loaded = 0
        results: List[Dict[str, Any]] = []

        # In real scraper: loop scrolling until enough items or end reached
        while total_loaded < max_items:
            _ = human_delay_ms(self.min_wait_ms, self.max_wait_ms)
            total_loaded += 1

        if seed_followers:
            logging.debug("Using provided seed_followers (%d)", len(seed_followers))
            records = seed_followers[:max_items]
        else:
            logging.debug("No seed_followers provided, fabricating sample data.")
            records = self._fabricate_sample(max_items)

        # Clean / normalize obvious text/url issues before schema normalization step
        cleaned: List[Dict[str, Any]] = []
        for r in records:
            cleaned.append(
                {
                    "id": clean_text(r.get("id")),
                    "image": clean_text(r.get("image")),
                    "title": clean_text(r.get("title") or r.get("name")),
                    "subtitle_text": clean_text(r.get("subtitle_text")),
                    "url": normalize_fb_url(r.get("url") or ""),
                    "friendship_status": clean_text(r.get("friendship_status") or "UNKNOWN"),
                    "gender": clean_text(r.get("gender")),
                    "name": clean_text(r.get("name") or r.get("title")),
                    "short_name": clean_text(r.get("short_name")),
                }
            )

        return cleaned
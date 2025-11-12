import random
import re
import time
from typing import Optional

def human_delay_ms(min_ms: int = 200, max_ms: int = 800) -> int:
    """Sleep for a pseudo-random human-like delay and return the delay in ms."""
    delay = random.randint(min_ms, max_ms)
    time.sleep(delay / 1000.0)
    return delay

def clean_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    # collapse whitespace
    s = re.sub(r"\s+", " ", s)
    return s or None

def normalize_fb_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    # Ensure protocol and canonical host
    if not url.startswith("http"):
        url = "https://" + url.lstrip("/")
    url = re.sub(r"^http://", "https://", url, flags=re.IGNORECASE)
    # Normalize known mobile/basic subdomains to www
    url = re.sub(r"^https://m\.facebook\.com", "https://www.facebook.com", url, flags=re.IGNORECASE)
    url = re.sub(r"^https://mbasic\.facebook\.com", "https://www.facebook.com", url, flags=re.IGNORECASE)
    url = re.sub(r"^https://facebook\.com", "https://www.facebook.com", url, flags=re.IGNORECASE)
    # Strip tracking params
    url = url.split("?")[0]
    return url
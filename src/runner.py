import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# Ensure we can import from src/ when running as a script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = CURRENT_DIR
ROOT_DIR = os.path.dirname(SRC_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from extractors.facebook_followers import FacebookFollowersExtractor  # type: ignore
from outputs.exporters import export_data  # type: ignore
from outputs.schema import Follower, normalize_record_list  # type: ignore

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def infer_output_dir(cli_outdir: Optional[str]) -> str:
    outdir = cli_outdir or os.path.join(ROOT_DIR, "data", "outputs")
    os.makedirs(outdir, exist_ok=True)
    return outdir

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Facebook Followers Scraper (demo runner). Normalizes follower data and exports in multiple formats."
    )
    p.add_argument(
        "--input",
        default=os.path.join(ROOT_DIR, "data", "inputs.sample.json"),
        help="Path to input JSON with keys: url (str), maxItems (int), seedFollowers (optional list[dict]).",
    )
    p.add_argument(
        "--settings",
        default=os.path.join(SRC_DIR, "config", "settings.example.json"),
        help="Path to settings JSON (delays, formats, etc.).",
    )
    p.add_argument(
        "--outdir",
        default=None,
        help="Directory to write outputs. Defaults to data/outputs/",
    )
    p.add_argument(
        "--formats",
        default=None,
        help="Comma-separated list of formats to export: json,jsonl,csv,xlsx. If omitted, uses settings.",
    )
    p.add_argument(
        "--base-name",
        default=None,
        help="Base file name without extension. Defaults to 'followers_<timestamp>'.",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    return p

def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    try:
        inputs: Dict[str, Any] = load_json(args.input)
    except FileNotFoundError:
        logging.error("Input file not found: %s", args.input)
        return 2
    except Exception as e:
        logging.exception("Failed to read input JSON: %s", e)
        return 2

    try:
        settings: Dict[str, Any] = load_json(args.settings)
    except FileNotFoundError:
        logging.warning("Settings file not found: %s; using defaults.", args.settings)
        settings = {}
    except Exception as e:
        logging.exception("Failed to read settings JSON: %s", e)
        return 2

    url: str = inputs.get("url", "")
    max_items: int = int(inputs.get("maxItems", 50))
    seed_followers: Optional[List[Dict[str, Any]]] = inputs.get("seedFollowers")

    extractor = FacebookFollowersExtractor(
        scroll_delay_ms=int(settings.get("delays", {}).get("scroll_ms", 600)),
        min_wait_ms=int(settings.get("delays", {}).get("min_wait_ms", 300)),
        max_wait_ms=int(settings.get("delays", {}).get("max_wait_ms", 900)),
    )

    logging.info("Running extractor for URL='%s' (maxItems=%d)", url, max_items)

    raw_records = extractor.run(url=url, max_items=max_items, seed_followers=seed_followers)
    logging.info("Extractor produced %d raw records", len(raw_records))

    normalized: List[Follower] = normalize_record_list(raw_records)
    logging.info("Normalized to %d schema-validated records", len(normalized))

    outdir = infer_output_dir(args.outdir)
    base_name = args.base_name or f"followers_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    formats = (
        [s.strip() for s in args.formats.split(",")]
        if args.formats
        else settings.get("export", {}).get("formats", ["json", "csv"])
    )

    logging.info("Exporting %d records to %s as %s", len(normalized), outdir, formats)
    export_data(normalized, outdir=outdir, base_name=base_name, formats=formats)

    logging.info("Done.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
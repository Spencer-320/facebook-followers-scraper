import csv
import json
import os
from typing import Iterable, List

from pydantic import BaseModel

def _to_dicts(models: Iterable[BaseModel]) -> List[dict]:
    return [m.model_dump() for m in models]

def _write_json(path: str, rows: List[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

def _write_jsonl(path: str, rows: List[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def _write_csv(path: str, rows: List[dict]) -> None:
    if not rows:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write("")  # empty file
        return
    fieldnames = sorted(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def _write_xlsx(path: str, rows: List[dict]) -> None:
    # Use pandas for quick xlsx
    import pandas as pd  # lazy import

    df = pd.DataFrame(rows)
    df.to_excel(path, index=False)

def export_data(models: Iterable[BaseModel], outdir: str, base_name: str, formats: List[str]) -> List[str]:
    """
    Export list of Pydantic models to multiple formats.
    Returns list of written file paths.
    """
    os.makedirs(outdir, exist_ok=True)
    rows = _to_dicts(models)
    written: List[str] = []
    for fmt in formats:
        fmt_lower = fmt.lower().strip()
        if fmt_lower == "json":
            path = os.path.join(outdir, f"{base_name}.json")
            _write_json(path, rows)
            written.append(path)
        elif fmt_lower == "jsonl":
            path = os.path.join(outdir, f"{base_name}.jsonl")
            _write_jsonl(path, rows)
            written.append(path)
        elif fmt_lower == "csv":
            path = os.path.join(outdir, f"{base_name}.csv")
            _write_csv(path, rows)
            written.append(path)
        elif fmt_lower == "xlsx":
            path = os.path.join(outdir, f"{base_name}.xlsx")
            _write_xlsx(path, rows)
            written.append(path)
        else:
            # silently skip unknown formats to keep runner simple
            continue
    return written
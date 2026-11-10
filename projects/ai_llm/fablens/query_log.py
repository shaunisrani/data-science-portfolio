"""Append-only JSONL query log for auditability: what was asked, which model, which sources, how long.
Set FABLENS_LOG to change the path; set FABLENS_LOG=off to disable. Questions can be redacted with FABLENS_LOG_REDACT=1."""
import hashlib
import json
import os
import time
from pathlib import Path

DEFAULT_PATH = Path(__file__).parent / "logs" / "queries.jsonl"


def log_query(**fields):
    path = os.getenv("FABLENS_LOG", str(DEFAULT_PATH))
    if path.lower() == "off":
        return None
    if os.getenv("FABLENS_LOG_REDACT") == "1" and "question" in fields:
        q = fields.pop("question")
        fields["question_sha256"] = hashlib.sha256(q.encode()).hexdigest()[:16]
    record = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **fields}
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return record

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["FABLENS_LOG"] = (str(Path(__file__).parent / "_test_queries.jsonl"))

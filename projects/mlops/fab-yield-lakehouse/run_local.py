"""Run the full pipeline locally (bronze -> silver -> gold -> train). On Databricks, the job in databricks.yml runs the same notebooks."""
import runpy
import sys
from pathlib import Path

NB = Path(__file__).parent / "notebooks"
sys.path.insert(0, str(NB))
for step in ["01_bronze_ingest", "02_silver_quality", "03_gold_features", "04_train_mlflow"]:
    print(f"\n=== {step} ===")
    runpy.run_path(str(NB / f"{step}.py"), run_name="__main__")

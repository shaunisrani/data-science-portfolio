# Databricks notebook source
# MAGIC %md
# MAGIC # 02 Silver: data quality checks and cleaning
# MAGIC Drops sensors that are mostly missing or constant and records every decision in a quality report.
# MAGIC Missing values stay null here; they are imputed inside the model pipeline using training wafers only (no test leakage).

# COMMAND ----------
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else ".")
from pyspark.sql import functions as F
from common import PROJECT, get_spark, read, write

MAX_MISSING = 0.5


def quality_checks(df):
    """Hard checks that stop the pipeline if the raw data is broken."""
    n = df.count()
    checks = {
        "row_count_is_1567": n == 1567,
        "labels_are_binary": set(r[0] for r in df.select("fail").distinct().collect()) <= {0, 1},
        "no_null_timestamps": df.filter(F.col("event_ts").isNull()).count() == 0,
        "wafer_id_unique": df.select("wafer_id").distinct().count() == n,
    }
    failed = [k for k, ok in checks.items() if not ok]
    if failed:
        raise ValueError(f"Data quality checks failed: {failed}")
    return checks


def clean(df):
    sensors = [c for c in df.columns if c.startswith("s") and c[1:].isdigit()]
    n = df.count()
    missing = df.select([(F.count(F.when(F.col(c).isNull() | F.isnan(c), c)) / n).alias(c) for c in sensors]).first().asDict()
    stds = df.select([F.stddev(c).alias(c) for c in sensors]).first().asDict()
    drop_missing = [c for c in sensors if missing[c] > MAX_MISSING]
    drop_constant = [c for c in sensors if c not in drop_missing and (stds[c] is None or stds[c] == 0)]
    keep = [c for c in sensors if c not in drop_missing + drop_constant]
    silver = df.select("wafer_id", "event_ts", "fail", *keep)
    report = {"rows": n, "sensors_in": len(sensors), "sensors_kept": len(keep),
              "dropped_mostly_missing": len(drop_missing), "dropped_constant": len(drop_constant),
              "fail_rate": round(df.filter("fail = 1").count() / n, 4)}
    return silver, report


# COMMAND ----------
if __name__ == "__main__":
    spark = get_spark()
    bronze = read(spark, "bronze", "secom")
    checks = quality_checks(bronze)
    silver, report = clean(bronze)
    write(silver, "silver", "secom")
    report["checks"] = checks
    (PROJECT / "reports").mkdir(exist_ok=True)
    (PROJECT / "reports" / "data_quality.json").write_text(json.dumps(report, indent=2))
    print("silver.secom:", report)

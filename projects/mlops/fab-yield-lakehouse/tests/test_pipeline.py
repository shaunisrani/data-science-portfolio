"""End-to-end pipeline test on the real SECOM data (local Spark, Parquet)."""
import os
import sys
from pathlib import Path

import pytest

NB = Path(__file__).resolve().parents[1] / "notebooks"
sys.path.insert(0, str(NB))


@pytest.fixture(scope="module")
def spark(tmp_path_factory):
    os.environ["LAKE_ROOT"] = str(tmp_path_factory.mktemp("lake"))
    import importlib
    import common
    importlib.reload(common)
    s = common.get_spark()
    yield s
    s.stop()


def load(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, NB / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_bronze_silver_gold(spark):
    bronze = load("01_bronze_ingest").ingest(spark)
    assert bronze.count() == 1567 and bronze.filter("fail = 1").count() == 104
    silver_mod = load("02_silver_quality")
    checks = silver_mod.quality_checks(bronze)
    assert all(checks.values())
    silver, report = silver_mod.clean(bronze)
    assert report["sensors_kept"] < 590 and report["dropped_mostly_missing"] > 0
    sensor_cols = [c for c in silver.columns if c.startswith("s") and c[1:].isdigit()]
    from pyspark.sql import functions as F
    assert silver.select([F.sum(F.col(c).isNull().cast("int")) for c in sensor_cols[:20]]).first() == tuple([0] * 20)
    gold = load("03_gold_features").build_gold(silver)
    train_max = gold.filter("split = 'train'").agg(F.max("event_ts")).first()[0]
    test_min = gold.filter("split = 'test'").agg(F.min("event_ts")).first()[0]
    assert train_max <= test_min  # no future data leaks into training


def test_quality_check_catches_bad_labels(spark):
    bronze = load("01_bronze_ingest").ingest(spark)
    from pyspark.sql import functions as F
    bad = bronze.withColumn("fail", F.lit(5))
    with pytest.raises(ValueError):
        load("02_silver_quality").quality_checks(bad)


def test_flagged_recall():
    import numpy as np
    fr = load("04_train_mlflow").flagged_recall
    y = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 1])
    s = np.array([.9, .1, .1, .1, .1, .1, .1, .1, .1, .2])
    assert fr(y, s, share=0.1) == 0.5

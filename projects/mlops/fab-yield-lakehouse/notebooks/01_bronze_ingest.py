# Databricks notebook source
# MAGIC %md
# MAGIC # 01 Bronze: ingest raw SECOM fab data
# MAGIC Raw sensor readings (1,567 wafers x 590 sensors) and pass/fail labels, kept as-is plus lineage columns.

# COMMAND ----------
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else ".")
from pyspark.sql import functions as F
from common import RAW_ROOT, get_spark, write

N_SENSORS = 590


def ingest(spark):
    sensors = (spark.read.csv(f"{RAW_ROOT}/secom.data", sep=" ", inferSchema=True, nanValue="NaN")
               .toDF(*[f"s{i:03d}" for i in range(N_SENSORS)]))
    labels = (spark.read.csv(f"{RAW_ROOT}/secom_labels.data", sep=" ", quote='"')
              .toDF("label_raw", "ts_raw"))

    def with_row_id(df):  # files are row-aligned; zipWithIndex keeps the original order
        return df.rdd.zipWithIndex().map(lambda r: (*r[0], r[1])).toDF([*df.columns, "wafer_id"])

    bronze = (with_row_id(labels).join(with_row_id(sensors), "wafer_id")
              .withColumn("fail", (F.col("label_raw").cast("int") == 1).cast("int"))
              .withColumn("event_ts", F.to_timestamp("ts_raw", "dd/MM/yyyy HH:mm:ss"))
              .withColumn("_ingested_at", F.current_timestamp())
              .withColumn("_source", F.lit("UCI SECOM"))
              .drop("label_raw", "ts_raw"))
    return bronze


# COMMAND ----------
if __name__ == "__main__":
    spark = get_spark()
    df = ingest(spark)
    write(df, "bronze", "secom")
    print(f"bronze.secom: {df.count()} rows, {len(df.columns)} columns")

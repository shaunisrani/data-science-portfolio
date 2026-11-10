# Databricks notebook source
# MAGIC %md
# MAGIC # 03 Gold: model-ready table with a time-based split
# MAGIC The earliest 75% of wafers train the model; the latest 25% test it, the way a model is used in a real fab.

# COMMAND ----------
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else ".")
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from common import get_spark, read, write

TRAIN_SHARE = 0.75


def build_gold(silver):
    ranked = silver.withColumn("time_rank", F.percent_rank().over(Window.orderBy("event_ts", "wafer_id")))
    return ranked.withColumn("split", F.when(F.col("time_rank") < TRAIN_SHARE, "train").otherwise("test")).drop("time_rank")


# COMMAND ----------
if __name__ == "__main__":
    spark = get_spark()
    gold = build_gold(read(spark, "silver", "secom"))
    write(gold, "gold", "secom_features")
    gold.groupBy("split").agg(F.count("*").alias("wafers"), F.sum("fail").alias("fails")).show()

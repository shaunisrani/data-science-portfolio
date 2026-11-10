# Databricks notebook source
"""Shared config. Runs on Azure Databricks (Delta tables on ADLS Gen2) or locally (Parquet files).

Environment:
  LAKE_ROOT   where bronze/silver/gold live. Local default: ./lake
              Azure example: abfss://lake@<storage-account>.dfs.core.windows.net/fab-yield
  RAW_ROOT    folder holding secom.data and secom_labels.data. Local default: ./data/raw
"""
import os
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1] if "__file__" in globals() else Path.cwd()
ON_DATABRICKS = "DATABRICKS_RUNTIME_VERSION" in os.environ
FORMAT = "delta" if ON_DATABRICKS else "parquet"
LAKE_ROOT = os.getenv("LAKE_ROOT", str(PROJECT / "lake"))
RAW_ROOT = os.getenv("RAW_ROOT", str(PROJECT / "data" / "raw"))


def table_path(layer, name):
    return f"{LAKE_ROOT}/{layer}/{name}"


def get_spark():
    if ON_DATABRICKS:
        from pyspark.sql import SparkSession

        return SparkSession.builder.getOrCreate()
    from pyspark.sql import SparkSession

    spark = (SparkSession.builder.master("local[2]").appName("fab-yield-lakehouse")
             .config("spark.sql.shuffle.partitions", "4").config("spark.ui.enabled", "false").getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def write(df, layer, name):
    df.write.mode("overwrite").format(FORMAT).save(table_path(layer, name))


def read(spark, layer, name):
    return spark.read.format(FORMAT).load(table_path(layer, name))

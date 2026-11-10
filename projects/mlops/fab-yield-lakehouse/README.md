# Fab Yield Lakehouse — Azure Databricks + MLflow

Predicts failing wafers from real semiconductor fab sensor data (UCI SECOM: 1,567 wafers × 590 sensors, 6.6% fail rate) with a medallion pipeline and governed model tracking.

## Pipeline

```
raw SECOM files
  → 01 Bronze  ingest as-is + lineage columns (source, ingest time)
  → 02 Silver  data-quality checks (stop the run if broken) + cleaning, logged to reports/data_quality.json
  → 03 Gold    model-ready table with a time-based train/test split (no future data in training)
  → 04 Train   2 models tracked in MLflow; best one registered in the model registry
```

Runs the same code in two places:

| | Local | Azure Databricks |
|---|---|---|
| Storage | Parquet in `./lake` | Delta tables on ADLS Gen2 (`abfss://…`) |
| Orchestration | `python run_local.py` | Databricks job from `databricks.yml` (Asset Bundle) |
| Tracking | MLflow (SQLite) | Databricks-managed MLflow / Unity Catalog |

**Azure ML**: to log runs to an Azure ML workspace instead, `pip install azureml-mlflow` and set `MLFLOW_TRACKING_URI` to the workspace's MLflow URI. The training code doesn't change.

## Governance

- **Data quality gates**: row count, binary labels, no missing timestamps, unique wafer IDs. The pipeline stops if any fail.
- **Every cleaning decision is recorded**: 28 of 590 sensors dropped for >50% missing values; the rest median-imputed.
- **Lineage**: every MLflow run is tagged with its source data and gold table; models are saved with an input/output signature and registered with a version number.
- **Safe model serialization**: models are saved with MLflow's skops format, trusting only the one sklearn type we trained ourselves.

## Results (time-based test set, 392 wafers, 24 fails)

| Model | ROC-AUC | PR-AUC | Fails caught reviewing riskiest 10% |
|---|---|---|---|
| Logistic regression (registered) | 0.67 | 0.10 | 21% (2× random) |
| Gradient boosting | 0.61 | 0.08 | 13% |

Random guessing gives PR-AUC ≈ 0.06 and catches 10% of fails. SECOM is a known hard dataset (few fails, noisy sensors), so the honest result is a modest lift. Next steps: feature selection, sensor-drift features, and threshold tuning with fab cost-of-miss vs. cost-of-review.

## Run

```
pip install -r requirements.txt     # needs Java for Spark
python run_local.py                 # full pipeline
python -m pytest -q tests           # end-to-end test on the real data
```

Deploy to Azure Databricks: fill in the workspace host and storage account in `databricks.yml`, then `databricks bundle deploy -t dev && databricks bundle run fab_yield_pipeline -t dev`.

## Data
UCI Machine Learning Repository, SECOM dataset (McCann & Johnston, 2008), CC BY 4.0. Label file SHA-256 matches the UCI original.

## Tech
PySpark · Delta Lake · Azure Databricks (Asset Bundles) · ADLS Gen2 · MLflow (tracking + registry) · Azure ML–compatible · scikit-learn · pytest

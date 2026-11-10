# Databricks notebook source
# MAGIC %md
# MAGIC # 04 Train: predict failing wafers, tracked and registered with MLflow
# MAGIC Compares two models on the time-based test set, logs params/metrics/data lineage, and registers the best one.

# COMMAND ----------
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else ".")
import mlflow
import numpy as np
from mlflow.models import infer_signature
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from common import ON_DATABRICKS, PROJECT, get_spark, read, table_path

MODEL_NAME = "fab_yield_fail_classifier"
FLAG_SHARE = 0.10  # flag the riskiest 10% of wafers for engineer review
# Types we trained ourselves and trust when saving with MLflow's safe (skops) serializer
TRUSTED = {"hist_gradient_boosting": ["sklearn.ensemble._hist_gradient_boosting.predictor.TreePredictor"]}

MODELS = {
    "logistic_regression": lambda: make_pipeline(StandardScaler(), LogisticRegression(C=0.01, class_weight="balanced", max_iter=2000)),
    "hist_gradient_boosting": lambda: HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200,
                                                                     class_weight="balanced", random_state=7),
}


def flagged_recall(y, scores, share=FLAG_SHARE):
    """Share of failing wafers caught if engineers review the top `share` of wafers by risk score."""
    k = max(1, int(round(share * len(scores))))
    top = np.argsort(-scores)[:k]
    return float(y[top].sum() / max(1, y.sum()))


def evaluate(model, X, y):
    s = model.predict_proba(X)[:, 1]
    return {"roc_auc": roc_auc_score(y, s), "pr_auc": average_precision_score(y, s),
            "recall_at_top10pct": flagged_recall(y, s), "fail_rate": float(y.mean())}


def load_xy(pdf):
    feats = [c for c in pdf.columns if c.startswith("s") and c[1:].isdigit()]
    tr, te = pdf[pdf.split == "train"], pdf[pdf.split == "test"]
    return feats, tr[feats].values, tr["fail"].values, te[feats].values, te["fail"].values


def train_all(pdf, experiment="fab-yield"):
    if not ON_DATABRICKS:
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", f"sqlite:///{PROJECT / 'mlflow.db'}"))
    mlflow.set_experiment(experiment)
    feats, Xtr, ytr, Xte, yte = load_xy(pdf)
    results = {}
    for name, make in MODELS.items():
        with mlflow.start_run(run_name=name) as run:
            model = make().fit(Xtr, ytr)
            m = evaluate(model, Xte, yte)
            mlflow.log_params({"model": name, "n_features": len(feats), "train_wafers": len(ytr),
                               "test_wafers": len(yte), "split": "time-based 75/25"})
            mlflow.log_metrics(m)
            mlflow.set_tags({"data.source": "UCI SECOM", "data.gold_table": table_path("gold", "secom_features")})
            mlflow.sklearn.log_model(model, name="model", signature=infer_signature(Xte[:5], model.predict_proba(Xte[:5])),
                                     **({"skops_trusted_types": TRUSTED[name]} if name in TRUSTED else {}))
            results[name] = {**m, "run_id": run.info.run_id}
    best = max(results, key=lambda k: results[k]["pr_auc"])
    version = mlflow.register_model(f"runs:/{results[best]['run_id']}/model", MODEL_NAME)
    return results, best, version.version


# COMMAND ----------
if __name__ == "__main__":
    spark = get_spark()
    pdf = read(spark, "gold", "secom_features").toPandas()
    results, best, version = train_all(pdf)
    summary = {"best_model": best, "registered": f"{MODEL_NAME} v{version}",
               "results": {k: {m: round(v, 3) for m, v in r.items() if m != "run_id"} for k, r in results.items()}}
    (PROJECT / "reports").mkdir(exist_ok=True)
    (PROJECT / "reports" / "model_results.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))

"""Stage 1 MLflow handoff test — verifies MLflow logs a test experiment.

Per L4.1 §2.3 Stage 1 handoff criterion 6: "MLflow tracking server logs a test experiment"
"""

import mlflow
import os

# Point to local MLflow backend
mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "file:///scratch/akula.pra/INTERCEPTA/mlflow")
mlflow.set_tracking_uri(mlflow_uri)
mlflow.set_experiment("intercepta_stage_1_smoke")

with mlflow.start_run(run_name="stage_1_smoke_test"):
    mlflow.log_param("stage", "1_foundation")
    mlflow.log_param("intercepta_version", "0.0.1.dev0")
    mlflow.log_metric("smoke_test_passed", 1.0)
    mlflow.log_text("Stage 1 smoke log entry.", "stage_1_message.txt")
    print(f"MLflow run logged successfully to {mlflow_uri}")
    print(f"Run ID: {mlflow.active_run().info.run_id}")

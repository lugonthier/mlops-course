import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd

MODEL_NAME = "ChurnPredictor"
MODEL_RUN_ID = "23a2419fc35d425980b6a15d239bc434"
client = MlflowClient()
mlflow.set_tracking_uri("http://127.0.0.1:5000")

# 1. Create the registered model
client.create_registered_model(MODEL_NAME)

model_version = client.create_model_version(
    name=MODEL_NAME,
    source=f"runs:/{MODEL_RUN_ID}/model",
    run_id=MODEL_RUN_ID,
    description="Model version created from run"
)

# 2. Set the alias and the validation status
client.set_registered_model_alias(MODEL_NAME, "candidate-latest", model_version.version)
client.set_model_version_tag(MODEL_NAME, model_version.version, "validation_status", "pending")

#### 3. SOME PROCESSES TO VALIDATE THE MODEL ####
model_to_validate_version = client.get_model_version_by_alias(MODEL_NAME, "candidate-latest")
client.set_model_version_tag(MODEL_NAME, model_to_validate_version.version, "validation_status", "approved")

#### 4. Promotion ####
model_to_promote_version = client.get_model_version_by_alias(MODEL_NAME, "candidate-latest")
client.set_registered_model_alias(MODEL_NAME, "production-live", model_to_promote_version.version)

#### 5. Get Production Model ####
production_model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}@production-live")

#### 6. Inference ####
data = pd.read_csv("data/churn_data_2025_05.csv")
X_test = data.drop(columns=["Churn"])
y_test = data["Churn"]

y_pred = production_model.predict(X_test)
print(y_pred)


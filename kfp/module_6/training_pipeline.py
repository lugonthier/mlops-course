import google.cloud.aiplatform as aip

from kfp import dsl, compiler
from typing import NamedTuple


@dsl.component(
    base_image="python:3.11",
    packages_to_install=[
        "fsspec",
        "gcsfs",
        "pandas",
        "scikit-learn",
    ],
)
def load_data(
    test_size_ratio: float,
    dataset_uri: str,
    x_train: dsl.Output[dsl.Dataset],
    y_train: dsl.Output[dsl.Dataset],
    x_test: dsl.Output[dsl.Dataset],
    y_test: dsl.Output[dsl.Dataset],
):
    import pandas as pd
    from sklearn.model_selection import train_test_split

    df = pd.read_csv(dataset_uri)
    x_train_df, x_test_df, y_train_df, y_test_df = train_test_split(
        df.drop(columns=["Churn"]),
        df["Churn"],
        test_size=test_size_ratio,
        random_state=42,
    )
    x_train_df.to_csv(x_train.path, index=False)
    y_train_df.to_csv(y_train.path, index=False)
    x_test_df.to_csv(x_test.path, index=False)
    y_test_df.to_csv(y_test.path, index=False)


@dsl.component(
    base_image="python:3.12", packages_to_install=["pandas", "scikit-learn", "mlflow"]
)
def train_model(
    x_train: dsl.Input[dsl.Dataset],
    y_train: dsl.Input[dsl.Dataset],
    x_test: dsl.Input[dsl.Dataset],
    y_test: dsl.Input[dsl.Dataset],
    metrics: dsl.Output[dsl.Metrics],
    model_name: str,
    mlflow_tracking_uri: str,
    mlflow_experiment_name: str,
) -> NamedTuple("outputs", accuracy=float):
    import mlflow
    import pandas as pd
    from mlflow.tracking import MlflowClient
    from sklearn.metrics import accuracy_score
    from sklearn.ensemble import RandomForestClassifier

    client = MlflowClient(tracking_uri=mlflow_tracking_uri)
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(mlflow_experiment_name)

    x_train_df = pd.read_csv(x_train.path)
    y_train_df = pd.read_csv(y_train.path)
    x_test_df = pd.read_csv(x_test.path)
    y_test_df = pd.read_csv(y_test.path)

    with mlflow.start_run() as run:
        model = RandomForestClassifier(n_estimators=5, max_depth=2, random_state=42)
        model.fit(x_train_df, y_train_df)
        mlflow.sklearn.log_model(model, "model", registered_model_name=model_name)

    run_id = run.info.run_id
    model_version = client.create_model_version(
        name=model_name,
        source=f"runs:/{run_id}/model",
        run_id=run_id,
        description="Model version created from run",
    )

    client.set_registered_model_alias(
        model_name, "candidate-latest", model_version.version
    )

    client.set_model_version_tag(model_name, model_version.version, "validation_status", "pending")

    accuracy = accuracy_score(y_test_df, model.predict(x_test_df))
    metrics.log_metric("accuracy", accuracy)
    return NamedTuple("outputs", accuracy=float)(accuracy)


@dsl.component(
    base_image="python:3.12", packages_to_install=["pandas", "scikit-learn", "mlflow"]
)
def evaluate_model(
    x_test: dsl.Input[dsl.Dataset],
    y_test: dsl.Input[dsl.Dataset],
    model_name: str,
    tracking_uri: str,
    metrics: dsl.Output[dsl.Metrics],
) -> NamedTuple("outputs", accuracy=float):
    import mlflow
    import pandas as pd
    from sklearn.metrics import accuracy_score

    x_test_df = pd.read_csv(x_test.path)
    y_test_df = pd.read_csv(y_test.path)
    mlflow.set_tracking_uri(tracking_uri)
    production_model = mlflow.pyfunc.load_model(f"models:/{model_name}@production-live")

    y_pred = production_model.predict(x_test_df)
    accuracy = accuracy_score(y_test_df, y_pred)
    metrics.log_metric("accuracy", accuracy)
    return NamedTuple("outputs", accuracy=float)(accuracy)


@dsl.component(base_image="python:3.12", packages_to_install=["mlflow"])
def promote_model(model_name: str, tracking_uri: str):

    from mlflow.tracking import MlflowClient

    client = MlflowClient(tracking_uri=tracking_uri)
    model_to_promote_version = client.get_model_version_by_alias(
        model_name, "candidate-latest"
    )
    client.set_registered_model_alias(
        model_name, "production-live", model_to_promote_version.version
    )
    client.set_model_version_tag(model_name, model_to_promote_version.version, "validation_status", "approved")


@dsl.pipeline
def training_pipeline(
    churn_dataset_uri: str,
    mlflow_tracking_uri: str,
    mlflow_experiment_name: str,
    model_name: str,
):
    load_data_task = load_data(test_size_ratio=0.2, dataset_uri=churn_dataset_uri)
    train_model_task = train_model(
        x_train=load_data_task.outputs["x_train"],
        y_train=load_data_task.outputs["y_train"],
        x_test=load_data_task.outputs["x_test"],
        y_test=load_data_task.outputs["y_test"],
        mlflow_tracking_uri=mlflow_tracking_uri,
        mlflow_experiment_name=mlflow_experiment_name,
        model_name=model_name,
    )

    evaluate_model_task = evaluate_model(
        x_test=load_data_task.outputs["x_test"],
        y_test=load_data_task.outputs["y_test"],
        model_name=model_name,
        tracking_uri=mlflow_tracking_uri,
    )
    with dsl.If(
        train_model_task.outputs["accuracy"] <= evaluate_model_task.outputs["accuracy"]
    ):
        promote_model_task = promote_model(
            model_name=model_name,
            tracking_uri=mlflow_tracking_uri,
        )


if __name__ == "__main__":

    PIPELINE_PACKAGE_PATH = "pipeline.yaml"
    
    LOCATION = "europe-west9"
    PROJECT_ID = "formation-mlops"
    compiler.Compiler().compile(
        training_pipeline,
        PIPELINE_PACKAGE_PATH,
        pipeline_parameters={
            "churn_dataset_uri": "gs://churn-datasets-mlops-training/churn_data_2025_03.csv",
            "mlflow_tracking_uri": "https://mlflow-server-instance-ezxhpzskva-od.a.run.app",
            "mlflow_experiment_name": "churn-rf-exp",
            "model_name": "ChurnPredictionv2",
        },
    )
    KFP_URL = "http://mrrwaapi.com/pipeline"
    import kfp

    client = kfp.Client(host=KFP_URL)
    client.create_run_from_pipeline_package(
        PIPELINE_PACKAGE_PATH,
        enable_caching=False,

    )
    
   
import google.cloud.aiplatform as aip

from kfp import dsl, compiler


@dsl.component(
    base_image="python:3.11",
    packages_to_install=[
        "fsspec",
        "gcsfs",
        "pandas",
        "scikit-learn",
    ],
)
def load_data(dataset_uri: str, features: dsl.Output[dsl.Dataset]):
    import pandas as pd

    df = pd.read_csv(dataset_uri)
    features_df = df.drop(columns=["Churn"])
    features_df.to_csv(features.path, index=False)


@dsl.component(
    base_image="python:3.11", packages_to_install=["pandas", "scikit-learn", "mlflow"]
)
def predict(
    features: dsl.Input[dsl.Dataset],
    model_name: str,
    tracking_uri: str,
    predictions: dsl.Output[dsl.Dataset],
):
    import pandas as pd
    import mlflow

    mlflow.set_tracking_uri(tracking_uri)

    production_model = mlflow.pyfunc.load_model(f"models:/{model_name}@production-live")

    features_df = pd.read_csv(features.path)
    pred = production_model.predict(features_df)
    predictions_df = pd.DataFrame(pred, columns=["prediction"])
    predictions_df.to_csv(predictions.path, index=False)


@dsl.pipeline(name="inference_pipeline")
def inference_pipeline(churn_dataset_uri: str, model_name: str, tracking_uri: str):
    load_data_task = load_data(dataset_uri=churn_dataset_uri)
    predict_task = predict(
        features=load_data_task.outputs["features"],
        model_name=model_name,
        tracking_uri=tracking_uri,
    )


if __name__ == "__main__":

    PIPELINE_PACKAGE_PATH = "pipeline.yaml"
    PIPELINE_ROOT_PATH = "gs://formation-mlops-kfp/pipeline_root"
    LOCATION = "europe-west9"
    PROJECT_ID = "formation-mlops"
    compiler.Compiler().compile(
        inference_pipeline,
        PIPELINE_PACKAGE_PATH,
        pipeline_parameters={
            "churn_dataset_uri": "gs://churn-datasets-mlops-training/churn_data_2025_05.csv",
            "model_name": "ChurnPrediction",
            "tracking_uri": "https://mlflow-server-instance-ezxhpzskva-od.a.run.app",
        },
    )
    aip.init(
        project=PROJECT_ID,
        location=LOCATION,
    )

    job = aip.PipelineJob(
        display_name=inference_pipeline.name,
        template_path=PIPELINE_PACKAGE_PATH,
        pipeline_root=PIPELINE_ROOT_PATH,
        location=LOCATION,
    )
    job.run(
        service_account=f"vertex-kfp@{PROJECT_ID}.iam.gserviceaccount.com",
    )

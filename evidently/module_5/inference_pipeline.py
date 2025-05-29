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
def load_data(
    dataset_uri: str, features: dsl.Output[dsl.Dataset], target: dsl.Output[dsl.Dataset]
):
    import pandas as pd

    df = pd.read_csv(dataset_uri)
    features_df = df.drop(columns=["Churn"])
    target_df = df[["Churn"]]
    features_df.to_csv(features.path, index=False)
    target_df.to_csv(target.path, index=False)


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


@dsl.component(
    base_image="python:3.12", packages_to_install=["pandas", "evidently==0.6.6"]
)
def data_quality(
    reference_features: dsl.Input[dsl.Dataset],
    current_features: dsl.Input[dsl.Dataset],
    report: dsl.Output[dsl.HTML],

):
    import pandas as pd
    from datetime import datetime
    from evidently.test_suite import TestSuite
    from evidently.ui.remote import RemoteWorkspace
    from evidently.test_preset import DataStabilityTestPreset

    reference_df = pd.read_csv(reference_features.path)
    current_df = pd.read_csv(current_features.path)
    test_suite = TestSuite(tests=[DataStabilityTestPreset()], timestamp=datetime.now(), tags=["data_quality_test_suite"])
    test_suite.run(reference_data=reference_df, current_data=current_df)
    test_suite.save(report.path)

@dsl.component(
    base_image="python:3.12", packages_to_install=["pandas", "evidently==0.6.6"]
)
def data_drift(
    reference_features: dsl.Input[dsl.Dataset],
    current_features: dsl.Input[dsl.Dataset],
    report: dsl.Output[dsl.HTML],

):
    import pandas as pd
    from datetime import datetime
    from evidently.report import Report
    from evidently.test_suite import TestSuite
    from evidently.metrics import DatasetDriftMetric
    from evidently.test_preset import DataDriftTestPreset

    reference_df = pd.read_csv(reference_features.path)
    current_df = pd.read_csv(current_features.path)
    test_suite = TestSuite(tests=[DataDriftTestPreset()], timestamp=datetime.now(), tags=["data_drift_test_suite"])
    report = Report(
        metrics=[
            DatasetDriftMetric(),
        ],
        tags=["data_drift"],
    )
    
    test_suite.run(reference_data=reference_df, current_data=current_df)
    report.run(reference_data=reference_df, current_data=current_df)
    test_suite.save(report.path)


@dsl.component(
    base_image="python:3.12", packages_to_install=["pandas", "evidently==0.6.6"]
)
def prediction_drift(
    reference_target: dsl.Input[dsl.Dataset],
    current_target: dsl.Input[dsl.Dataset],
    drift_report: dsl.Output[dsl.HTML],

):
    import pandas as pd
    from datetime import datetime
    from evidently.report import Report
    from evidently.metrics import ColumnDriftMetric


    reference_df = pd.read_csv(reference_target.path)
    current_df = pd.read_csv(current_target.path)
    report = Report(
        metrics=[ColumnDriftMetric(column_name="prediction")], timestamp=datetime.now(), tags=["prediction_drift"]
    )
    report.run(reference_data=reference_df, current_data=current_df)
    report.save(drift_report.path)

@dsl.component(
    base_image="python:3.12", packages_to_install=["pandas", "evidently==0.6.6"]
)
def post_process(
    features: dsl.Input[dsl.Dataset],
    target: dsl.Input[dsl.Dataset],
    predictions: dsl.Input[dsl.Dataset],
    output_dataset: dsl.Output[dsl.Dataset],
):
    import pandas as pd

    df = pd.read_csv(features.path)
    df["predictions"] = pd.read_csv(predictions.path)
    df["Churn"] = pd.read_csv(target.path)
    df.to_csv(output_dataset.path, index=False)


@dsl.pipeline(name="inference_pipeline")
def inference_pipeline(
    churn_dataset_uri: str,
    model_name: str,
    tracking_uri: str,
    reference_dataset_uri: str,
    workspace: str,
    project_id: str,
):
    load_reference_data_task = load_data(
        dataset_uri=reference_dataset_uri
    ).set_display_name("Load Reference Data")
    load_data_task = load_data(dataset_uri=churn_dataset_uri).set_display_name(
        "Load Current Data"
    )
    data_quality_task = data_quality(
        reference_features=load_reference_data_task.outputs["features"],
        current_features=load_data_task.outputs["features"],
        workspace=workspace,
        project_id=project_id,
    ).set_display_name("Data Quality")
    data_drift_task = data_drift(
        reference_features=load_reference_data_task.outputs["features"],
        current_features=load_data_task.outputs["features"],
        workspace=workspace,
        project_id=project_id,
    ).set_display_name("Data Drift")

    predict_current_task = predict(
        features=load_data_task.outputs["features"],
        model_name=model_name,
        tracking_uri=tracking_uri,
    ).set_display_name("Predict Current")

    # If Reference Predictions weren't saved, we need to predict them
    predict_reference_task = predict(
        features=load_reference_data_task.outputs["features"],
        model_name=model_name,
        tracking_uri=tracking_uri,
    ).set_display_name("Predict Reference")

    target_drift_task = prediction_drift(
        reference_target=predict_reference_task.outputs["predictions"],
        current_target=predict_current_task.outputs["predictions"],
        workspace=workspace,
        project_id=project_id,
    ).set_display_name("Target Drift")

    post_process_task = post_process(
        features=load_data_task.outputs["features"],
        target=load_data_task.outputs["target"],
        predictions=predict_current_task.outputs["predictions"],
    ).set_display_name("Post Process")


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
            "reference_dataset_uri": "gs://churn-datasets-mlops-training/churn_data_2025_03.csv",
            # "workspace": "https://evidently-server-instance-988498511057.europe-west9.run.app",
            # "project_id": "01971bcb-7cfc-7619-be16-58ac37370ed4",
        },
    )
    KFP_URL = "http://mrrwaapi.com/pipeline"
    import kfp

    client = kfp.Client(host=KFP_URL)
    client.create_run_from_pipeline_package(
        PIPELINE_PACKAGE_PATH,
        enable_caching=False,

    )

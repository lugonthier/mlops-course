import google.cloud.aiplatform as aip

from kfp import dsl
from kfp import compiler

@dsl.component(base_image="python:3.12")
def get_current_model_metrics() -> float:
    return 0.8


@dsl.component(base_image="python:3.12")
def get_candidate_model_metrics() -> float:
    return 0.9


@dsl.component(base_image="python:3.12")
def evaluate_promotion_candidate(current_model_accuracy: float, candidate_model_accuracy: float, min_required_accuracy: float) -> bool:
    return candidate_model_accuracy > current_model_accuracy and candidate_model_accuracy >= min_required_accuracy

@dsl.component(base_image="python:3.12")
def promote_candidate_model() -> None:
    print("Promoting candidate model")

@dsl.component(base_image="python:3.12")
def reject_candidate_model() -> None:
    print("Rejecting candidate model")
    
    
@dsl.pipeline
def model_promotion_decision_pipeline():
    current_model_accuracy = get_current_model_metrics()
    candidate_model_accuracy = get_candidate_model_metrics()
    evaluate_candidate_op = evaluate_promotion_candidate(current_model_accuracy=current_model_accuracy.output, candidate_model_accuracy=candidate_model_accuracy.output, min_required_accuracy=0.8)
    with dsl.If(evaluate_candidate_op.output == True):
        promote_candidate_model()
    with dsl.Else():
        reject_candidate_model()

if __name__ == "__main__":
    PIPELINE_PACKAGE_PATH = "pipeline.yaml"
    PIPELINE_ROOT_PATH = "gs://formation-mlops-kfp/pipeline_root"
    LOCATION = "europe-west9"
    PROJECT_ID = "formation-mlops"
    compiler.Compiler().compile(model_promotion_decision_pipeline, PIPELINE_PACKAGE_PATH)
    aip.init(
        project=PROJECT_ID,
        location=LOCATION,
    )

    job = aip.PipelineJob(
        display_name=model_promotion_decision_pipeline.name,
        template_path=PIPELINE_PACKAGE_PATH,
        pipeline_root=PIPELINE_ROOT_PATH,
        location=LOCATION,
        enable_caching=False,
    )
    job.run(
        service_account=f"vertex-kfp@{PROJECT_ID}.iam.gserviceaccount.com",
    )

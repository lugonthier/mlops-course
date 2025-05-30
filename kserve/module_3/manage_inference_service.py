from kubernetes import client
from kserve import (
    V1beta1InferenceService,
    V1beta1InferenceServiceSpec,
    V1beta1PredictorSpec,
    constants,
    KServeClient,
)


def create_inference_service(
    image_uri: str, service_name: str, namespace: str = None
) -> V1beta1InferenceService:
    default_model_spec = V1beta1InferenceServiceSpec(
        predictor=V1beta1PredictorSpec(
            containers=[
                client.V1Container(
                    name="kserve-container",
                    image=image_uri,
                    args=["--protocol=v2"],
                    ports=[
                        client.V1ContainerPort(
                            name="http1", container_port=8080, protocol="TCP"
                        )
                    ],
                    env=[
                        client.V1EnvVar(
                            name="PROTOCOL", value="v2"
                        ),
                        client.V1EnvVar(name="MLFLOW_TRACKING_URI", value="http://host.docker.internal:5002"),
                    ],
                )
            ],
        )
    )
    isvc = V1beta1InferenceService(
        api_version=constants.KSERVE_V1BETA1,
        kind=constants.KSERVE_KIND_INFERENCESERVICE,
        metadata=client.V1ObjectMeta(name=service_name, namespace=namespace),
        spec=default_model_spec,
    )
    return isvc


if __name__ == "__main__":
    import os
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--inference_service_name", type=str, required=True)
    parser.add_argument("--inference_service_namespace", type=str)
    parser.add_argument("--image_uri", type=str)
    parser.add_argument(
        "--operation",
        type=str,
        choices=["create", "get", "replace", "delete"],
        required=True,
    )
    args = parser.parse_args()

    isvc = create_inference_service(
        image_uri=os.getenv("KSERVE_SERVING_IMAGE", args.image_uri),
        service_name=args.inference_service_name,
        namespace=args.inference_service_namespace,
    )

    kserve_client = KServeClient()

    if args.operation == "create":
        kserve_client.create(isvc, watch=True)

    elif args.operation == "get":
        kserve_client.get(
            name=args.inference_service_name,
            namespace=args.inference_service_namespace,
            watch=True,
        )

    elif args.operation == "replace":
        kserve_client.replace(
            name=args.inference_service_name,
            inferenceservice=isvc,
            namespace=args.inference_service_namespace,
            watch=True,
        )

    elif args.operation == "delete":
        kserve_client.delete(
            name=args.inference_service_name, namespace=args.inference_service_namespace
        )

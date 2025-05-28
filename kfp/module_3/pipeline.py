from kfp import dsl


@dsl.container_component
def write_to_file_container(text_to_write: str, output_file: dsl.OutputPath(str)):
    """A container component that writes text to a file."""
    command_string = (
        f"mkdir -p $(dirname '{{{{$.outputs.parameters['output_file'].output_file}}}}') && "
        f"echo '{{{{$.inputs.parameters['text_to_write']}}}}' > '{{{{$.outputs.parameters['output_file'].output_file}}}}'"
    )
    
    return dsl.ContainerSpec(
        image="alpine", command=["sh", "-c"], args=[command_string]
    )


@dsl.pipeline(
    name="container-pipeline",
    description="A pipeline demonstrating a container component.",
)
def container_pipeline(message: str = "Hello from container component!"):
    """Pipeline that uses the containerized component."""
    write_task = write_to_file_container(text_to_write=message)


if __name__ == "__main__":
    KFP_URL = "http://mrrwaapi.com/pipeline"
    import kfp

    client = kfp.Client(host=KFP_URL)

    print(
        client.create_run_from_pipeline_func(
            container_pipeline,
            arguments={"message": "Hello from container component!"},
            experiment_name="lucas",
        )
    )

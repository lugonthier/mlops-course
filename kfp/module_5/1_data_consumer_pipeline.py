import google.cloud.aiplatform as aip
from kfp import dsl
from kfp import compiler


@dsl.component(base_image="python:3.12", packages_to_install=["pandas", "scikit-learn"])
def produce_data(out_dataset: dsl.Output[dsl.Dataset]):
    from sklearn.datasets import load_iris
    import pandas as pd

    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["target"] = pd.Series(iris.target)
    df.to_csv(out_dataset.path, index=False)


@dsl.component(base_image="python:3.12", packages_to_install=["pandas"])
def consume_data(in_dataset: dsl.Input[dsl.Dataset]):
    import pandas as pd

    df = pd.read_csv(in_dataset.path)
    print(df.describe())


@dsl.pipeline
def data_pipeline():
    produce_data_op = produce_data()
    consume_data_op = consume_data(in_dataset=produce_data_op.outputs["out_dataset"])



if __name__ == "__main__":
    KFP_URL = "http://mrrwaapi.com/pipeline"
    import kfp

    client = kfp.Client(host=KFP_URL)
    
    client.create_run_from_pipeline_func(
        data_pipeline,
        arguments={},
        experiment_name="lucas",
    )
    
 

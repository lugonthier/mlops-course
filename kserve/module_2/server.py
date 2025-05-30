import mlflow

from typing import Dict
from kserve import InferRequest, InferResponse, InferOutput, Model, ModelServer
from kserve.utils.utils import get_predict_input, generate_uuid


class SampleModel(Model):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.load()

    def load(self):

        self.model = mlflow.pyfunc.load_model(f"models:/{self.name}@production-live")
        self.ready = True

    def predict(
        self, payload: InferRequest, headers: Dict[str, str] = None
    ) -> InferResponse:
        
        input_features = get_predict_input(
            payload,
        )
        response_id = generate_uuid()

        result = self.model.predict(input_features)

        infer_output = InferOutput(
            name="output-0", shape=list(result.shape), datatype="INT64", data=result
        )
        infer_response = InferResponse(
            model_name=self.name, infer_outputs=[infer_output], response_id=response_id
        )
        return infer_response


if __name__ == "__main__":
    model = SampleModel("ChurnPrediction")
    ModelServer().start([model])

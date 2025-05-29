# Custom KServe Service

This module explores how to create your own custom serving runtime if KServe's prebuilt runtimes are not suitable for your needs. This is useful when you have complex preprocessing/postprocessing, specific dependencies, or require particular optimizations.

## 1. Implement Your Custom Model Server

You'll need to write a Python class that inherits from `kserve.Model` and implements at least the `load` and `predict` methods.

### Key Methods:
-   `__init__(self, name: str)`: Constructor for your model server. Call `super().__init__(name)` and `self.load()`.
-   `load(self)`: Implement logic to load your model into memory. Set `self.ready = True` upon successful loading.
-   `predict(self, payload: kserve.InferRequest, headers: Dict[str, str] = None) -> kserve.InferResponse`: Implement the core inference logic. This method receives an `InferRequest` (which can be a dictionary or raw bytes depending on your setup) and should return an `InferResponse`.
-   `preprocess(self, payload: kserve.InferRequest, headers: Dict[str, str] = None) -> kserve.InferRequest` (Optional): Implement any preprocessing logic before the `predict` method is called.
-   `postprocess(self, response: kserve.InferResponse, headers: Dict[str, str] = None) -> kserve.InferResponse` (Optional): Implement any postprocessing logic after the `predict` method.

### Example Structure (`model.py`):

```python
from typing import Dict
from kserve import Model, ModelServer, InferRequest, InferResponse

class MyCustomModel(Model):
    def __init__(self, name: str):
       super().__init__(name)
       self.name = name
       self.load()

    def load(self):
      # TODO: Implement your model loading logic here
      # e.g., self.model = joblib.load('model.pkl')
      print(f"Model {self.name} loaded.")
      self.ready = True
    
    def predict(self, payload: InferRequest, headers: Dict[str, str] = None) -> InferResponse:
        # TODO: Implement your prediction logic
        # 1. Extract inputs from payload.inputs or payload (if raw request)
        #    raw_data = payload # if using raw request bytes
        #    deserialized_data = self.decode_request(payload) # if using kserve.InferInput
        #    input_data = [infer_input.data for infer_input in payload.inputs if infer_input.name == "your_input_name"]

        # 2. Perform inference using self.model
        #    predictions = self.model.predict(processed_input)

        # 3. Format the output as kserve.InferResponse
        #    infer_output = kserve.InferOutput(name="output-0", shape=list(predictions.shape), datatype="FP32", data=predictions.tolist())
        #    return InferResponse(model_name=self.name, infer_outputs=[infer_output])

        # Example for a simple pass-through or echo
        print(f"Received payload: {payload}")
        return InferResponse(model_name=self.name, response=payload, infer_outputs=[]) # Adjust as needed

    # Optional: Implement preprocess
    # def preprocess(self, payload: InferRequest, headers: Dict[str, str] = None) -> InferRequest:
    #     # TODO: Implement preprocessing
    #     print(f"Preprocessing payload: {payload}")
    #     return payload

    # Optional: Implement postprocess
    # def postprocess(self, response: InferResponse, headers: Dict[str, str] = None) -> InferResponse:
    #     # TODO: Implement postprocessing
    #     print(f"Postprocessing response: {response}")
    #     return response

if __name__ == "__main__":

  model = MyCustomModel("my-custom-churn-model")
  ModelServer().start([model])
```

**Exercise:**
-   Adapt the `MyCustomModel` class to serve your churn prediction model.
-   Implement the `load` method to load your serialized churn model.
-   Implement the `predict` method to handle incoming requests, make predictions, and return them in the expected format.
-   Consider if `preprocess` or `postprocess` steps are needed for your model.

## 2. Build Your Serving Environment (Docker Image)

Create a `Dockerfile` to package your model server code, dependencies, and model artifacts.

### Example `Dockerfile`:

```Dockerfile
FROM python:3.12-slim-bullseye

WORKDIR /app


COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY model.py model.py

ENTRYPOINT ["python", "model.py"] 

EXPOSE 8080
```

**Exercise:**
-   Create a `requirements.txt` file for your churn model server.
-   Write a `Dockerfile` to build an image for your custom server.
-   Ensure your model artifacts are included in the image or loaded from a remote source in your `load()` method.

### Build and Push the Image:
Build your Docker image and push it to an image registry (e.g., Docker Hub, GCR, ECR).
```bash
docker build -t <your-registry>/<your-image-name>:<tag> .
docker push <your-registry>/<your-image-name>:<tag>
```
Replace `<your-registry>/<your-image-name>:<tag>` with your actual image URI.

## 3. Create the `InferenceService` Resource

Define an `InferenceService` YAML that uses your custom container image.

### Kubernetes Secret for Image Pull (If Private Registry):
If your image is in a private registry, create a Kubernetes secret:
```bash
kubectl create secret docker-registry your-registry-secret \
    --docker-server=<your-registry-server> \
    --docker-username=<your-username> \
    --docker-password=<your-password-or-token> \
    --docker-email=<your-email>
    # For GCR using a service account key:
    # --docker-server=<LOCATION>-docker.pkg.dev/<PROJECT-ID>/<REPOSITORY> \
    # --docker-username=_json_key \
    # --docker-password="$(cat path/to/your/sa-key.json)"
```

### Example `custom-churn-isvc.yaml`:

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: custom-churn-predictor # Choose a name
  # namespace: your-namespace   # Optional
spec:
  predictor:
    # Uncomment and set if using a private registry
    # imagePullSecrets:
    #   - name: your-registry-secret 
    containers:
      - name: kserve-container # KServe convention, can be customized
        image: <your-registry>/<your-image-name>:<tag> # Your custom image URI
```

**Exercise:**
-   Create the `InferenceService` YAML file for your custom churn model server.
-   Make sure to use the correct image URI you pushed.
-   If you used a private registry, include the `imagePullSecrets` section.

## 4. Apply and Test

Apply the `InferenceService` manifest:
```bash
kubectl apply -f custom-churn-isvc.yaml
```

Then, check its status and test it as described in Module 1 (sections 4 and 5). The key difference is that KServe will now use your custom-built Docker image to serve the model.
Make sure your `predict` method in your custom model server correctly handles the input format you send and produces the output format KServe expects or that your client can parse.
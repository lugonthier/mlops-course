# Inference Service (YAML)

This module focuses on deploying a model (e.g., a churn prediction model) using KServe's standard runtimes and a YAML `InferenceService` Custom Resource Definition (CRD).

## 1. Understanding Standard KServe Predictors

KServe provides out-of-the-box runtimes for common model formats. Key examples include:

| Name                      | Supported Model Formats |
| ------------------------- | ----------------------- |
| `kserve-tensorflow-serving` | TensorFlow              |
| `kserve-torchserve`         | PyTorch                 |
| `kserve-sklearnserver`      | SKLearn                 |

Refer to the [official KServe documentation](https://kserve.github.io/website/0.11/modelserving/servingruntimes/) for a full list.

## 2. Define Your `InferenceService`

Create a YAML file (e.g., `churn-model-isvc.yaml`) to define your `InferenceService`.

**Option A: Explicitly Specify Runtime**

You can explicitly name the runtime if you know which one to use:

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: churn-predictor
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      storageUri: gs://model-registry-mlops-formation/model.pkl 
      runtime: kserve-sklearnserver 
```

**Option B: Let KServe Auto-Select Runtime**

KServe can also automatically select a compatible runtime based on the `modelFormat.name`:

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: churn-predictor
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn # KServe will look for a runtime supporting sklearn
      storageUri: gs://model-registry-mlops-formation/model.pkl
```

**Note:** For your churn prediction model, you will need to:
-   Replace `churn-predictor` with an appropriate name.
-   Specify the correct `modelFormat` (e.g., `sklearn`, `tensorflow`, `pytorch`, `onnx`, `triton`).
-   Update `storageUri` to point to where your churn model is stored (e.g., an S3 bucket, GCS bucket, or a PVC).
-   If your model requires specific environment variables or resources, add them to the predictor spec.

## 3. Apply the `InferenceService`

Once your YAML file is ready, apply it to your Kubernetes cluster:

```bash
kubectl apply -f churn-model-isvc.yaml
```

## 4. Check Deployment Status

Verify that your `InferenceService` is deployed and ready:

```bash
kubectl get inferenceservice churn-predictor
```

Look for the `READY` status to be `True`.

## 5. Test Your Deployed Model

Follow similar steps to those in Module 0 (section 3.3) to test your deployed churn model endpoint. You will need to:
1.  Ensure port-forwarding to the Istio ingress gateway is active.
2.  Identify your service's hostname.
3.  Construct a JSON payload appropriate for your churn model's input.
4.  Use `curl` or another HTTP client to send a prediction request to the `/v1/models/your-service-name:predict` endpoint.
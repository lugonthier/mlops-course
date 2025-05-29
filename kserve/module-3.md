# KServe SDK

This module demonstrates how to use the KServe Python SDK to define and deploy your `InferenceService`. This approach is beneficial for integrating model deployment into ML pipelines or managing KServe resources programmatically.



## 1. Define the `InferenceService` in Python

Instead of YAML, you can define the `InferenceService` spec using Python objects provided by the KServe SDK.

### Example for a Custom Model:
This example assumes you have a custom model image (like the one built in Module 2).

```python
from kubernetes import client as k8s_client # Alias to avoid confusion with KServeClient
from kserve import (
    V1beta1InferenceService,
    V1beta1InferenceServiceSpec,
    V1beta1PredictorSpec,
    constants,
    KServeClient
)

# Configuration
MODEL_NAME = "custom-churn-sdk"  # Choose a name for your InferenceService
MODEL_IMAGE_URI = "<your-registry>/<your-image-name>:<tag>" # Replace with your custom image URI
NAMESPACE = "default"  # Or your target namespace
KUBE_CONTEXT = None # Or specify your kubeconfig context if not default
KUBE_CONFIG_FILE = None # Or specify path to your kubeconfig file

# Define the predictor spec for your custom container
default_model_spec = V1beta1InferenceServiceSpec(
    predictor=V1beta1PredictorSpec(

        containers=[
            k8s_client.V1Container(
                name="kserve-container", # Standard KServe container name
                image=MODEL_IMAGE_URI,

            )
        ]
    )
)

# Create the InferenceService object
isvc = V1beta1InferenceService(
    api_version=constants.KSERVE_V1BETA1,
    kind=constants.KSERVE_KIND,
    metadata=k8s_client.V1ObjectMeta(
        name=MODEL_NAME,
        namespace=NAMESPACE

    ),
    spec=default_model_spec
)

print(f"InferenceService spec for '{MODEL_NAME}' prepared.")
```

### Example for a Standard KServe Runtime (e.g., Scikit-learn):
If you want to use a standard runtime (like in Module 1) but define it via SDK:

```python
MODEL_NAME_SKLEARN = "sklearn-churn-sdk"
MODEL_STORAGE_URI = "s3://your-bucket/path/to/your/churn-model.joblib"
NAMESPACE = "default"

sklearn_predictor_spec = V1beta1PredictorSpec(
    model=V1beta1ModelSpec(
        model_format=V1beta1ModelFormat(name="sklearn"),
        storage_uri=MODEL_STORAGE_URI
    )
)

default_model_spec_sklearn = V1beta1InferenceServiceSpec(predictor=sklearn_predictor_spec)

isvc_sklearn = V1beta1InferenceService(
    api_version=constants.KSERVE_V1BETA1,
    kind=constants.KSERVE_KIND,
    metadata=k8s_client.V1ObjectMeta(
        name=MODEL_NAME_SKLEARN,
        namespace=NAMESPACE
    ),
    spec=default_model_spec_sklearn
)
print(f"InferenceService spec for '{MODEL_NAME_SKLEARN}' (sklearn) prepared.")
```

**Exercise:**
-   Modify the Python code to define an `InferenceService` for your churn prediction model.
    -   If using your custom image from Module 2, ensure `MODEL_IMAGE_URI` is correct and uncomment/configure `imagePullSecrets` if needed.
    -   If you prefer to use a standard KServe runtime (like `kserve-sklearnserver`), adapt the second example, ensuring `MODEL_STORAGE_URI` points to your model.
-   Set the `MODEL_NAME` and `NAMESPACE` appropriately.

## 2. Use the `KServeClient` to Manage the `InferenceService`

The `KServeClient` allows you to create, get, update, patch, or delete `InferenceService` resources.

```python
# Initialize KServeClient
# You can specify kubeconfig context or file if not using the default
kserve_client = KServeClient(
    context=KUBE_CONTEXT, 
    config_file=KUBE_CONFIG_FILE
)

# --- Create or Update Operation ---
try:
    # Try to get the InferenceService, if it exists, we might update or patch
    kserve_client.get(MODEL_NAME, namespace=NAMESPACE)
    print(f"InferenceService '{MODEL_NAME}' already exists. Patching...")
    # If it exists and you want to update it (replace the whole spec):
    # kserve_client.replace(MODEL_NAME, isvc, namespace=NAMESPACE, watch=True, timeout_seconds=120)
    # Or patch it (only apply changes, more common for updates):
    kserve_client.patch(MODEL_NAME, isvc, namespace=NAMESPACE, watch=True, timeout_seconds=120)
    print(f"InferenceService '{MODEL_NAME}' patched.")
except RuntimeError as e:
    if "not found" in str(e).lower(): # A bit simplistic check, k8s client might raise specific exceptions
        print(f"InferenceService '{MODEL_NAME}' not found. Creating...")
        kserve_client.create(isvc, namespace=NAMESPACE, watch=True, timeout_seconds=120)
        print(f"InferenceService '{MODEL_NAME}' created.")
    else:
        print(f"Error checking/creating InferenceService: {e}")
        raise

# --- Get Operation ---
print(f"\nFetching details for '{MODEL_NAME}'...")
deployed_isvc = kserve_client.get(MODEL_NAME, namespace=NAMESPACE)
print(deployed_isvc)
# You can check status: deployed_isvc.status.url, deployed_isvc.status.conditions

# --- Delete Operation (Uncomment to use) ---
# print(f"\nDeleting InferenceService '{MODEL_NAME}'...")
# kserve_client.delete(MODEL_NAME, namespace=NAMESPACE)
# print(f"InferenceService '{MODEL_NAME}' deleted.")
```

**Explanation:**
-   `KServeClient()`: Initializes the client. It will use your default kubeconfig context unless specified.
-   `kserve_client.create(isvc, ...)`: Creates the `InferenceService` on the cluster.
    -   `watch=True`: Waits for the `InferenceService` to become ready.
    -   `timeout_seconds`: Sets a timeout for the watch operation.
-   `kserve_client.get(...)`: Retrieves an existing `InferenceService`.
-   `kserve_client.patch(MODEL_NAME, isvc, ...)`: Applies changes to an existing `InferenceService`. This is generally preferred over `replace` for updates as it's more declarative.
-   `kserve_client.replace(MODEL_NAME, isvc, ...)`: Replaces the entire existing `InferenceService` spec with the new one.
-   `kserve_client.delete(...)`: Deletes the `InferenceService`.

**Exercise:**
-   Combine the definition code with the client management code into a single Python script.
-   Run the script to deploy your churn model `InferenceService`.
-   Verify the deployment using `kubectl get inferenceservices`.
-   Test the endpoint as in previous modules.
-   Experiment with updating a field (e.g., an annotation or an environment variable if using a custom container) and re-running the script with `patch` or `replace`.
-   Finally, uncomment and use the `delete` operation to clean up the `InferenceService`.

## Important Considerations:
-   **Namespaces:** Always be mindful of the Kubernetes namespace you are working in.
-   **Error Handling:** The example provides basic error handling. For production pipelines, more robust error checking and exception handling are recommended.
-   **Authentication:** Ensure your Python environment has the necessary credentials to interact with your Kubernetes cluster (usually via `kubeconfig`).
-   **Idempotency:** The provided create/patch logic attempts to be idempotent (safe to run multiple times). You might refine this based on your specific needs.
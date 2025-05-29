# Installation

This module guides you through the local installation of KServe.

## Prerequisites

Ensure you have the following tools installed:
- Docker ([installation guide](https://docs.docker.com/engine/install/))
- Kind ([installation guide](https://kind.sigs.k8s.io/docs/user/quick-start))
- Kubernetes CLI (kubectl) ([installation guide](https://kubernetes.io/docs/tasks/tools/))

## 1. Create a Kubernetes Cluster

Use Kind to create a local Kubernetes cluster:
```bash
kind create cluster
```

After creation, set `kubectl` to use the new cluster's context:
```bash
kubectl config use-context kind-kind
```

## 2. Install KServe

Execute the KServe quick install script:
```bash
curl -s "https://raw.githubusercontent.com/kserve/kserve/release-0.11/hack/quick_install.sh" | bash
```

## 3. Verify Installation (Optional)

To ensure KServe is working correctly, you can deploy a sample model.

### 3.1 Create a Test Namespace
```bash
kubectl create namespace kserve-test
```

### 3.2 Deploy a Sample InferenceService
```bash
kubectl apply -n kserve-test -f - <<EOF
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "sklearn-iris"
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      storageUri: "gs://kfserving-examples/models/sklearn/1.0/model"
EOF
```

Check the deployment status:
```bash
kubectl get inferenceservices sklearn-iris -n kserve-test
```

### 3.3 Test the Sample Endpoint

1.  **Set up port forwarding:**
    Open a terminal and run:
    ```bash
    INGRESS_GATEWAY_SERVICE=$(kubectl get svc --namespace istio-system --selector="app=istio-ingressgateway" --output jsonpath='{.items[0].metadata.name}')
    kubectl port-forward --namespace istio-system svc/${INGRESS_GATEWAY_SERVICE} 8080:80
    ```

2.  **Send a prediction request:**
    Open another terminal and run:
    ```bash
    export INGRESS_HOST=localhost
    export INGRESS_PORT=8080

    cat <<EOF > "./iris-input.json"
    {
      "instances": [
        [6.8,  2.8,  4.8,  1.4],
        [6.0,  3.4,  4.5,  1.6]
      ]
    }
    EOF

    SERVICE_HOSTNAME=$(kubectl get inferenceservice sklearn-iris -n kserve-test -o jsonpath='{.status.url}' | cut -d "/" -f 3)

    curl -v -H "Host: ${SERVICE_HOSTNAME}" -H "Content-Type: application/json" "http://${INGRESS_HOST}:${INGRESS_PORT}/v1/models/sklearn-iris:predict" -d @./iris-input.json
    ```
    If you see predictions in the output, KServe is installed and working.
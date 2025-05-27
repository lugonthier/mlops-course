# mlops-course

Installer kind:
https://kind.sigs.k8s.io/docs/user/quick-start/

Installer kubectl:
https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/

Install KFP:
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=2.5.0"
kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/dev?ref=2.5.0"

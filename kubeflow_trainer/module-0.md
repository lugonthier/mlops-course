
Créer le cluster :
```bash
kind create cluster
```

Install Kubeflow Trainer Controller Manager
```bash
kubectl apply --server-side -k "https://github.com/kubeflow/trainer.git/manifests/overlays/manager?ref=master"
```

Check si tout est ok :
```bash
kubectl get pods -n kubeflow-system
```

Install Training Runtime :
```bash
kubectl apply --server-side -k "https://github.com/kubeflow/trainer.git/manifests/overlays/runtimes?ref=master"
```
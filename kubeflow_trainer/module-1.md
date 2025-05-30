# 1 - Définir la fonction d'entraînement PyTorch
Avant de créer un `TrainJob` Kubeflow, il est essentiel de définir la fonction d'entraînement. Cette fonction encapsule toute la logique d'entraînement du modèle, du chargement des données à l'optimisation. 
Chaque nœud PyTorch participant à l'entraînement exécutera cette fonction. 
Kubeflow Trainer se charge de mettre en place l'environnement distribué nécessaire pour PyTorch, notamment pour l'utilisation du Distributed Data Parallel (DDP).

```python
def train_pytorch():
    import os

    import torch
    from torch import nn
    import torch.nn.functional as F

    from torchvision import datasets, transforms
    import torch.distributed as dist
    from torch.utils.data import DataLoader, DistributedSampler

    # [1] Configure CPU/GPU device and distributed backend.
    # Kubeflow Trainer will automatically configure the distributed environment.
    device, backend = ("cuda", "nccl") if torch.cuda.is_available() else ("cpu", "gloo")
    dist.init_process_group(backend=backend)

    local_rank = int(os.getenv("LOCAL_RANK", 0))
    print(
        "Distributed Training with WORLD_SIZE: {}, RANK: {}, LOCAL_RANK: {}.".format(
            dist.get_world_size(),
            dist.get_rank(),
            local_rank,
        )
    )

    # [2] Define PyTorch CNN Model to be trained.
    class Net(nn.Module):
        def __init__(self):
            super(Net, self).__init__()
            self.conv1 = nn.Conv2d(1, 20, 5, 1)
            self.conv2 = nn.Conv2d(20, 50, 5, 1)
            self.fc1 = nn.Linear(4 * 4 * 50, 500)
            self.fc2 = nn.Linear(500, 10)

        def forward(self, x):
            x = F.relu(self.conv1(x))
            x = F.max_pool2d(x, 2, 2)
            x = F.relu(self.conv2(x))
            x = F.max_pool2d(x, 2, 2)
            x = x.view(-1, 4 * 4 * 50)
            x = F.relu(self.fc1(x))
            x = self.fc2(x)
            return F.log_softmax(x, dim=1)

    # [3] Attach model to the correct device.
    device = torch.device(f"{device}:{local_rank}")
    model = nn.parallel.DistributedDataParallel(Net().to(device))
    model.train()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1, momentum=0.9)

    # [4] Get the Fashion-MNIST dataset and distributed it across all available devices.
    dataset = datasets.FashionMNIST(
        "./data",
        train=True,
        download=True,
        transform=transforms.Compose([transforms.ToTensor()]),
    )
    train_loader = DataLoader(
        dataset,
        batch_size=100,
        sampler=DistributedSampler(dataset),
    )

    # [5] Define the training loop.
    for epoch in range(3):
        for batch_idx, (inputs, labels) in enumerate(train_loader):
            # Attach tensors to the device.
            inputs, labels = inputs.to(device), labels.to(device)

            # Forward pass
            outputs = model(inputs)
            loss = F.nll_loss(outputs, labels)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            if batch_idx % 10 == 0 and dist.get_rank() == 0:
                print(
                    "Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}".format(
                        epoch,
                        batch_idx * len(inputs),
                        len(train_loader.dataset),
                        100.0 * batch_idx / len(train_loader),
                        loss.item(),
                    )
                )

    # Wait for the training to complete and destroy to PyTorch distributed process group.
    dist.barrier()
    if dist.get_rank() == 0:
        print("Training is finished")
    dist.destroy_process_group()
```

# 2 - Vérifier les Runtimes d'entraînement Kubeflow disponibles
Avant de soumettre la tâche, vous pouvez lister les environnements d'exécution (Runtimes) disponibles pour l'entraînement avec Kubeflow.
```python
from kubeflow.trainer import TrainerClient, CustomTrainer

for r in TrainerClient().list_runtimes():
    print(f"Runtime: {r.name}")
```

# 3 - Créer un TrainJob
Maintenant, nous allons créer un `TrainJob` en utilisant le runtime `torch-distributed`. Ce runtime est spécifiquement conçu pour les entraînements distribués PyTorch. Dans cet exemple, nous allons configurer l'entraînement pour s'exécuter sur 1 seul nœud PyTorch.

```python
job_id = TrainerClient().train(
    trainer=CustomTrainer(
        func=train_pytorch,
        num_nodes=1,
        resources_per_node={
            "cpu": 2,
            "memory": "8Gi",
        },
    ),
    runtime=TrainerClient().get_runtime("torch-distributed"),
)
```

# 4 - Consulter les logs d'entraînement
Une fois le TrainJob soumis, vous pouvez suivre sa progression en consultant les logs.
```python
logs = TrainerClient().get_job_logs(name=job_id)
```

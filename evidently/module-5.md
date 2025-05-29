# Monitoring avec un Dashboard

Construire un dashboard pour le monitoring a plusieurs avantages :

- Lorsqu'on déploit plusieurs modèle en production, on veut généralement, une vue en temps réel de comment les modèles performent.
- On veut connaître cette performance et comment elle évolue à travers le temps. Ce qu'offre difficilement un monitoring comme dans le module 4.

## 1. Intégration d'un dashboard dans un système ML.

Remplacer la couche de monitoring précédente par un dashboard.

Pour cela vous aves un workspace evidently déployé [ici](https://evidently-server-instance-988498511057.europe-west9.run.app).

Ajouter un dashboard en roulant le script `evidently/module_5/batch_monitoring.py`, n'oubliez pas de remplacer le nom du projet (variable `YOUR_PROJECT_NAME`).

Une fois le projet créer, allez sur le server pour récupérer son ID que nous utiliserons pour stocker les reports et tests.

Pour vous y connecter au workspace :
```python
from evidently.ui.remote import RemoteWorkspace
ws = RemoteWorkspace(workspace)
project = ws.get_project(project_id)
```
Pour ajouter un rapport:

```python
ws.add_report(project.id, report)
```

Pour ajouter un test suite:
```python
ws.add_test_suite(project.id, test_suite)
```

Vous pouvez maintenant modifier votre (ou vos) pipeline(s) pour centraliser votre monitoring.
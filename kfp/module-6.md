# Projet ML avec KFP et MLflow

L'objectif de cette partie est de construire un projet ML de bout en bout, en utilisant KFP pour l'orchestration et MLflow pour le suivi des expériences et la gestion des modèles.

## 1 - Configuration du Projet - Cas d'Usage ML Simple

En utilisant Le dataset de Churn, nous pouvons nous concentrer sur l'orchestration KFP et l'intégration MLOps avec MLflow, plutôt que sur la complexité du modèle ML lui-même.

### 1.1 - Définir le problème ML et le dataset

- **Problème :** Classification binaire pour la prédiction du churn.
- **Dataset :** Le dataset se situe dans le dossier `data`. Il est simple, ne nécessite pas de nettoyage complexe et est bien adapté pour un premier projet.

### 1.2 - Créer un composant KFP de chargement et de prétraitement des données

Ce composant sera responsable du chargement des données, de leur division en ensembles d'entraînement et de test, et de la sortie de ces ensembles en tant qu'artefacts KFP.

1. Créez un nouveau fichier Python
2. Définissez un composant `load_and_preprocess_data`.
- Utilisez `@dsl.component`. Spécifiez une image de base et les `packages_to_install` nécessaires (par exemple, `scikit-learn`, `pandas`).
- Le composant prendra un `test_size_ratio: float` en entrée.
- Il sortira quatre artefacts de type 'Dataset' : `x_train`, `y_train`, `x_test`, `y_test`. Ces `dsl.Dataset` pointeront vers des fichiers (par exemple, CSV) contenant les données.

```python
    import pandas as pd
    from sklearn.model_selection import train_test_split

    df = pd.read_csv(dataset_uri)
    x_train_df, x_test_df, y_train_df, y_test_df = train_test_split(
        df.drop(columns=["Churn"]),
        df["Churn"],
        test_size=test_size_ratio,
        random_state=42,
    )
```

Un workflow ML typique (charger, prétraiter, entraîner, évaluer, inférer)  se traduit naturellement en une séquence de composants KFP. Cela renforce l'idée que KFP est un outil pour structurer et automatiser ces étapes standard.


## 2 - Construction et Suivi de la Pipeline d'Entraînement avec MLflow

MLflow permet de découpler le suivi des expériences de l'orchestration KFP. KFP gère l'exécution des étapes, tandis que MLflow gère la journalisation et l'organisation des métadonnées ML. `MLFLOW_TRACKING_URI` est le lien critique entre ces deux systèmes.

**Tableau : API MLflow Clés pour KFP**

| API MLflow                     | Objectif dans un Composant KFP                                                              |
|--------------------------------|---------------------------------------------------------------------------------------------|
| `mlflow.set_tracking_uri(uri)` | Spécifie l'URL du serveur de suivi MLflow à utiliser.                                         |
| `mlflow.set_experiment(name)`  | Définit l'expérience active sous laquelle les exécutions (runs) seront journalisées.        |
| `with mlflow.start_run():`     | Démarre un nouveau run MLflow ; les logs se font dans ce contexte.                             |
| `mlflow.log_param(key, value)` | Journalise un hyperparamètre ou un paramètre d'entrée.                                        |
| `mlflow.log_metric(key, value)`| Journalise une métrique de performance (par exemple, accuracy, loss).                         |
| `mlflow.sklearn.log_model(model, path)` | Journalise un modèle scikit-learn, incluant ses dépendances et sa signature.                |
| `mlflow.register_model(uri, name)` | Enregistre une version de modèle dans le Registre de Modèles MLflow.                        |
| `mlflow.sklearn.load_model(uri)` | Charge un modèle scikit-learn depuis un URI MLflow (run ou registre).                       |

### 2.1 - Créer un composant KFP d'entraînement de modèle avec MLflow

Ce composant prendra les données d'entraînement, entraînera un classifieur simple (par exemple, LogisticRegression), et utilisera MLflow pour journaliser les informations pertinentes.

1. Définissez un composant `train_model`.

   - Entrées : `x_train: dsl.Input[dsl.Dataset]`, `y_train: dsl.Input[dsl.Dataset]`, `mlflow_tracking_uri: str`, `mlflow_experiment_name: str`, et des hyperparamètres pour le modèle (par exemple, C: float).
   - Sortie KFP (optionnelle mais recommandée pour la lignée) : `output_model: dsl.Output[dsl.Model]` pour une copie du modèle comme artefact KFP.
   - Sortie Python (recommandée) : L'URI du modèle MLflow (str) pour faciliter son utilisation par les étapes suivantes.

Lors de l'utilisation de MLflow, le modèle devient principalement un "artefact MLflow" stocké via `mlflow.sklearn.log_model` dans le backend d'artefacts de MLflow. Bien que l'on puisse aussi sortir le modèle comme un artefact KFP standard , la source de vérité pour le modèle devient MLflow, surtout si l'on utilise ensuite le registre MLflow.
Exemple :
```python
   import mlflow
   import pandas as pd
   from mlflow.tracking import MlflowClient
   from sklearn.metrics import accuracy_score
   from sklearn.ensemble import RandomForestClassifier

   client = MlflowClient(tracking_uri=mlflow_tracking_uri)
   mlflow.set_tracking_uri(mlflow_tracking_uri)
   mlflow.set_experiment(mlflow_experiment_name)

   x_train_df = pd.read_csv(x_train.path)
   y_train_df = pd.read_csv(y_train.path)
   x_test_df = pd.read_csv(x_test.path)
   y_test_df = pd.read_csv(y_test.path)

   with mlflow.start_run() as run:
      model = RandomForestClassifier(n_estimators=5, max_depth=2, random_state=42)
      model.fit(x_train_df, y_train_df)
      mlflow.sklearn.log_model(model, "model", registered_model_name=model_name)

   run_id = run.info.run_id
   model_version = client.create_model_version(
      name=model_name,
      source=f"runs:/{run_id}/model",
      run_id=run_id,
      description="Model version created from run",
   )

   client.set_registered_model_alias(
      model_name, "candidate-latest", model_version.version
   )

   client.set_model_version_tag(model_name, model_version.version, "validation_status", "pending")

   accuracy = accuracy_score(y_test_df, model.predict(x_test_df))
   metrics.log_metric("accuracy", accuracy)
```


### 2.2 - Assembler et exécuter la pipeline d'entraînement complète

1. Définissez une pipeline KFP `training_pipeline` qui orchestre `load_and_preprocess_data` et `train_model`.
   - Passez les sorties de données du premier composant aux entrées du second.
   - Passez les paramètres `mlflow_tracking_uri` et `mlflow_experiment_name` à la pipeline, qui les transmettra au composant d'entraînement.

2. Préparez votre environnement MLflow
   - Si vous n'avez pas de serveur MLflow, vous pouvez en lancer un localement.
   - Assurez-vous que l'URI de suivi dans votre pipeline KFP pointe vers ce serveur et qu'il est accessible depuis l'environnement d'exécution de vos composants KFP (par exemple, si KFP s'exécute dans Docker ou Kubernetes, localhost pourrait ne pas être accessible de la même manière ; utilisez l'IP de la machine hôte ou configurez le réseau Docker/Kubernetes).

3. Compilez et exécutez cette pipeline sur votre backend KFP.
4. Vérifiez l'UI MLflow : Vous devriez voir une nouvelle expérience, un nouveau run, avec les paramètres, métriques et le modèle enregistrés.

Utiliser MLflow instance:
```python
   compiler.Compiler().compile(
      training_pipeline,
      PIPELINE_PACKAGE_PATH,
      pipeline_parameters={
         "churn_dataset_uri": "gs://churn-datasets-mlops-training/churn_data_2025_03.csv",
         "mlflow_tracking_uri": "https://mlflow-server-instance-ezxhpzskva-od.a.run.app",
         "mlflow_experiment_name": "",
         "model_name": "",
      },
   )
```

## 3 - Construction et Exécution de la Pipeline d'Inférence

Passer l'URI MLflow (soit l'URI du run, soit l'URI du modèle enregistré) du composant d'entraînement au composant d'inférence est la méthode la plus directe et robuste pour assurer la lignée du modèle.

### 3.1 - Créer un composant KFP pour charger un modèle et faire des prédictions

Ce composant chargera un modèle depuis MLflow en utilisant son URI et effectuera des prédictions sur de nouvelles données.

1. Définissez un composant pour loader le modèle et un composant d'inférence.

### 3.2 - Assembler et exécuter la pipeline d'inférence

Pour cet exercice, nous allons créer une pipeline d'inférence distincte qui prend l'URI du modèle en entrée.

1. Définissez une pipeline d'inférence.


## 4 - Implémentation de l'Entraînement Continu et Promotion de Modèle

Une stratégie de promotion de modèle dans un contexte MLOps implique une évaluation automatisée suivie d'une action conditionnelle (enregistrement et assignation d'alias/tag dans MLflow Model Registry), orchestrée par KFP.

### 4.1 - Ajouter un composant KFP d'évaluation de modèle

Ce composant évaluera le modèle entraîné sur l'ensemble de test et sortira les métriques.

1. Définissez un composant d'évaluation

### 4.2 - Implémenter une stratégie de promotion de modèle

Si le modèle est satisfaisant, nous l'enregistrons dans le Registre de Modèles MLflow et lui assignons un alias. 

1. Définissez un composant chargé d'enregister le modèle dans le registre et si nécessaire de le promouvoir.
2. Mettez à jour votre pipeline d'entraînement pour inclure ces étapes.
3. Compilez et exécutez cette pipeline complète sur votre backend KFP.
4. Vérifiez l'UI MLflow :
   - Le modèle devrait être enregistré dans le Registre de Modèles.
   - Une nouvelle version devrait exister.
   - L'alias spécifié devrait pointer vers cette nouvelle version si la condition de promotion a été remplie.

Pour un véritable entraînement continu, les pipelines KFP doivent être conçues pour être paramétrables (par exemple, pour spécifier les sources de données) et idempotentes. La planification elle-même est généralement gérée par un ordonnanceur externe ou les fonctionnalités de "Recurring Runs" de KFP.
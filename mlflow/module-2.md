## Packager en tant que Projet MLflow

**Objectif :** Transformer l'exercice de tracking précédent en un projet MLflow reproductible.

## 1 Créer la Structure du Projet

- Créez un nouveau répertoire, par exemple iris_mlflow_project/.
- Déplacez votre script d'entraînement précédent (celui qui utilise mlflow.log_param, mlflow.log_metric, etc.) dans ce répertoire et renommez-le `train.py`.

## 2 - Modifier `train.py` pour Accepter les Arguments
- Importez le module `argparse`.
- Créez un `ArgumentParser`.
- Ajoutez des arguments pour les hyperparamètres que vous souhaitez rendre configurables (par exemple, `--C` pour la régression logistique, `--n_estimators`, `--max_depth` pour RandomForest). Définissez leur type (float, int) et éventuellement une valeur par défaut.

- Ajoutez un argument pour le chemin des données, par exemple --data_path.
- Parsez les arguments en début de script.
- Utilisez les valeurs des arguments dans votre code au lieu des valeurs codées en dur. Assurez-vous que les paramètres passés à `mlflow.log_params()` reflètent bien les arguments reçus.

## 3 - Créer le FIchier `conda.yaml`

- À la racine de `iris_mlflow_project/`, créez un fichier `conda.yaml`.
- Spécifiez un nom pour l'environnement (par exemple, `iris_project_env`).
- Ajoutez les canaux nécessaires (par exemple, `conda-forge`, `defaults`).
- Listez les dépendances : python (avec une version spécifique, par exemple python=3.12), pip, et sous pip:, listez `mlflow`, `scikit-learn`, `pandas`, `matplotlib`, `seaborn`. Utilisez des versions spécifiques (par exemple, scikit-learn==1.2.2) pour garantir la reproductibilité.

## 4 - Créer le Fichier MLproject

- À la racine de `iris_mlflow_project/`, créez un fichier `MLproject`.
- Ajoutez une clé `name:` (par exemple, name: Iris Classifier Project).
- Ajoutez la clé `conda_env: conda.yaml`.
- Définissez un point d'entrée, par exemple main: :
  - Sous `main:`, ajoutez `parameters:`.
  - Déclarez les paramètres que vous avez ajoutés à `train.py` via argparse. Par exemple :
  ```yaml
  parameters:
  C: {type: float, default: 1.0}
  data_path: {type: path, default: "../data/iris.csv"} # Exemple de chemin par défaut
  ```
  Assurez-vous que les types (float, path, etc.) correspondent.
  - Ajoutez la clé `command:` et spécifiez comment lancer votre script en utilisant les paramètres. Par exemple :
  ```yaml
  command: "python train.py --C {C} --data_path {data_path}"
  ```

## 5 - Exécuter le Projet

- Ouvrez un terminal et naviguez à l'intérieur du répertoire `iris_mlflow_project/`.
- Exécution avec les valeurs par défaut : Lancez `mlflow run .` (le . indique le répertoire courant). MLflow devrait :
    - Lire `MLproject`.
    - Créer (ou réutiliser) l'environnement Conda défini dans `conda.yaml` (cela peut prendre un peu de temps la première fois).
    - Exécuter la commande `main` avec les valeurs par défaut des paramètres.
    - Enregistrer un nouveau run dans MLflow Tracking.
- Exécution avec des paramètres personnalisés : Lancez `mlflow run . -P C=0.5 -P data_path=/path/to/your/iris_data.csv` (adaptez les paramètres et le chemin). MLflow utilisera les valeurs fournies.
- (Optionnel : Exécution depuis Git) Si votre projet est sur GitHub, essayez de l'exécuter directement depuis l'URI Git : `mlflow run https://github.com/your_user/iris_mlflow_project.git -P C=0.1`.


## 6 - Vérifier dans l'UI MLflow

- Lancez `mlflow ui` (si ce n'est pas déjà fait).
- Allez à l'expérience "Iris Classification Basics".
- Vérifiez que les nouveaux runs apparaissent.
- Pour chaque run lancé via `mlflow run`, vérifiez que :
  - Les paramètres enregistrés correspondent bien aux valeurs par défaut ou à celles passées avec `-P`.
  - La section "Source" du run indique le nom du projet et le point d'entrée (`main`). Si exécuté depuis Git, le commit hash doit être présent.
  - Les métriques et artefacts sont enregistrés comme prévu.

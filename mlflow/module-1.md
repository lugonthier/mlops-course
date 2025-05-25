# Enregistrer une Expérience

**Objectif :** Acquérir une première expérience pratique avec l'API MLflow Tracking pour enregistrer les éléments essentiels d'une expérience de machine learning.

**Dataset :** Pour cette première pratique, nous utiliserons le dataset classique Iris. Il est simple, bien connu et permet de se concentrer sur les mécanismes de MLflow.


## 1 - Mise en Place

- Importez les bibliothèques nécessaires : `mlflow`, `sklearn.datasets`, `sklearn.model_selection`, `sklearn.metrics` (par exemple, accuracy_score, f1_score), pandas (pour input_example),` matplotlib.pyplot` et `seaborn`.
  
- Définissez l'URI du serveur de suivi. Pour commencer, utilisons le stockage local par défaut : mlflow.set_tracking_uri("./mlruns"). 
  
- Définissez un nom pour votre expérience en utilisant `mlflow.set_experiment`.


## 2 - Préparation des Données :

- Chargez le dataset Iris.
- Divisez les données en ensembles d'entraînement et de test.


## 3 - Script d'Entraînement et Logging MLflow :

- Définissez quelques hyperparamètres à tester. Par exemple, votre modèle.
- Démarrez un run MLflow en utilisant le gestionnaire de contexte : `with mlflow.start_run`: Utilisez `run_name` pour donner un nom descriptif à votre run.
- Enregistrez les hyperparamètres : Utilisez `mlflow.log_params(params)`.
- Entraînez le modèle : Créez une instance de votre modèle avec les params définis et entraînez-le sur vos données d'entraînement.
- Évaluez le modèle : Faites des prédictions sur les données de test et calculez des métriques comme l'accuracy et le F1-score.
- Enregistrez les métriques (`mlflow.log_metric`).


## 4 - Enregistrez le modèle
- Utilisez `mlflow.sklearn.log_model`.
- Spécifiez le modèle entraîné.
- Donnez un artifact_path. Ce sera le nom du dossier dans les artefacts du run.
- Fournissez un input_example (par exemple, X_train[:5]) pour que MLflow infère la signature.   
- Ajoutez registered_model_name="IrisClassifier" pour enregistrer directement le modèle dans le registre (nous explorerons le registre plus tard).

## 5 Enregistrer un Graphique
- Générez une matrice de confusion à partir des prédictions (y_test, y_pred). - - Utilisez matplotlib ou seaborn pour la visualiser.
- Sauvegardez la figure dans un fichier image local.
- Enregistrez ce fichier comme artefact `mlflow.log_artifact`.
N'oubliez pas `plt.close()` pour éviter d'afficher le graphique dans la sortie du script si ce n'est pas souhaité.   
## 6 Vérification

- Modifiez les hyperparamètres (par exemple, changez la valeur de C) et le run_name, puis réexécutez le script plusieurs fois.
- Ouvrez un terminal dans le répertoire où vous avez exécuté le script.
- Lancez l'interface utilisateur MLflow : mlflow ui.
- Ouvrez votre navigateur et allez à l'adresse indiquée (généralement http://127.0.0.1:5000).
- Naviguez vers l'expérience "Iris Classification Basics".

- Allez voir la liste des runs avec leurs noms, paramètres et métriques.
- Sélectionner plusieurs runs et cliquer sur "Compare" pour voir un tableau comparatif détaillé.
- Cliquez sur un run spécifique pour voir tous les détails, y compris les paramètres, les métriques, les tags, et la section "Artifacts".
- Explorez les artefacts : montrez le dossier du modèle (logistic_regression_model) contenant MLmodel, model.pkl, conda.yaml, requirements.txt, python_env.yaml, et signature.json. 
  
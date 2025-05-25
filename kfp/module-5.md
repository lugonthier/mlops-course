# Fonctionnalités Clés de KFP

Ces fonctionnalités sont les briques de base qui permettent de construire des workflows ML complexes de manière modulaire et réutilisable.

## 1 - Passage d'artefacts et de paramètres entre composants

Les composants communiquent en se passant des données (artefacts) et des valeurs simples (paramètres).

1. Créez un nouveau script.
2. Définissez deux composants : `produce_data` et `consume_data`.
- `produce_data` :
   - Charge les données iris depuis `sklearn`.
   - Sort un artefact de type `Dataset` qui sera transmit au composant suivant.
- `consume_data` :
   - Prend l'artefact `Dataset` en entrée.
   - Affiche des statistiques sur les données.

## 2 - Implémenter l'exécution conditionnelle avec `dsl.If` et `dsl.Else` pour la promotion de modèles

KFP permet d'exécuter des parties de votre pipeline conditionnellement (`dsl.If`, `dsl.Elif`, `dsl.Else`). Un cas d'usage courant est la promotion d'un nouveau modèle en production seulement s'il surpasse le modèle actuel et atteint un certain seuil de performance. Dans cet exemple, nous supposons que les métriques des modèles (comme l'accuracy) sont disponibles, potentiellement issues d'étapes précédentes du pipeline ou de systèmes externes.

1. Définissez les composants suivants :

- `get_current_model_metrics`:
    - Simule la récupération des métriques du modèle actuellement en production.
    - Pourrait prendre un identifiant de modèle ou une configuration en entrée.
    - Sort un paramètre `current_model_accuracy: float`.
- `get_candidate_model_metrics`:
    - Simule la récupération des métriques d'un modèle candidat à la promotion.
    - Pourrait prendre un identifiant de modèle ou une configuration en entrée.
    - Sort un paramètre `candidate_model_accuracy: float`.
- `evaluate_promotion_candidate`:
    - Prend en entrée `current_model_accuracy: float`, `candidate_model_accuracy: float`, et `min_required_accuracy: float`.
    - Retourne `True` si `candidate_model_accuracy > current_model_accuracy` ET `candidate_model_accuracy >= min_required_accuracy`, sinon `False`.
- `promote_candidate_model`:
    - Affiche un message indiquant que le modèle candidat est promu.
    - Dans un cas réel, ce composant pourrait copier les artefacts du modèle vers un emplacement de production, mettre à jour une configuration de service, etc.
- `reject_candidate_model`:
    - Affiche un message indiquant que le modèle candidat est rejeté et que le modèle actuel est conservé.

2. Définissez une pipeline `model_promotion_decision_pipeline` qui utilise ces composants.
   
- Exécutez `get_current_model_metrics` et `get_candidate_model_metrics`.
- Le composant `evaluate_promotion_candidate` prendra en entrée les accuracies obtenues et un `param_min_required_accuracy` défini au niveau de la pipeline.
- Utilisez `dsl.If(evaluate_candidate_task.output == True)` (ou simplement `dsl.If(evaluate_candidate_task.output)`) pour exécuter `promote_candidate_model`. Donnez un nom à ce bloc, par exemple `dsl.If(..., name="promote_candidate_if_better_and_meets_threshold")`.
- Utilisez `dsl.Else(name="reject_candidate_otherwise")` pour exécuter `reject_candidate_model`.

3. Testez localement en variant les paramètres d'accuracy fournis (ou simulés par les composants `get_..._metrics`), ainsi que `param_min_required_accuracy`, pour observer les deux branches de décision (promotion ou rejet).

## 3 - Implémenter les boucles avec `dsl.ParallelFor` pour le réglage d'hyperparamètres

`dsl.ParallelFor` est idéal pour des tâches comme le *grid search* d'hyperparamètres, où vous souhaitez entraîner et évaluer un modèle avec différentes combinaisons de paramètres en parallèle. Chaque itération de la boucle peut correspondre à un jeu d'hyperparamètres.

**Cas d'usage : Grid search sur un hyperparamètre d'un modèle linéaire pour le dataset Iris.**

1.  **Définissez un composant `train_evaluate_linear_model_on_iris`** :
    *   Prend en entrée les paramètres suivants, qui seront fournis par chaque item de la boucle `dsl.ParallelFor`:
        *   `hyperparam_name: str` : Le nom de l'hyperparamètre (par exemple, `"C"`).
        *   `hyperparam_value: float` : La valeur de l'hyperparamètre à tester (par exemple, la force de régularisation `C` pour une `LogisticRegression`).
    *   Actions :
        *   Charge le dataset Iris (`sklearn.datasets.load_iris`).
        *   Divise les données en ensembles d'entraînement et de test.
        *   Entraîne un modèle `sklearn.linear_model.LogisticRegression` en utilisant la `hyperparam_value` fournie pour le paramètre `C`.
        *   Évalue le modèle sur l'ensemble de test (par exemple, calcule l'accuracy).
    *   Sorties :
        *   `tested_hyperparam_name: str`
        *   `tested_hyperparam_value: float`
        *   `model_accuracy: float`

2.  **Définissez une pipeline `iris_hyperparam_search_pipeline`** :
    *   Créez une liste de dictionnaires d'hyperparamètres à tester. Chaque dictionnaire contient le nom et la valeur de l'hyperparamètre.
        Par exemple : `hyperparams_to_search = [{'name': 'C', 'value': 0.1}, {'name': 'C', 'value': 1.0}, {'name': 'C', 'value': 10.0}]`
    *   Utilisez `dsl.ParallelFor(items=hyperparams_to_search, name="grid_search_loop") as hp_config_item:`.
        Le `name` ici est pour la lisibilité dans l'UI de KFP.
    *   À l'intérieur de la boucle, appelez le composant `train_evaluate_linear_model_on_iris`.
        *   Passez les valeurs du dictionnaire `hp_config_item` aux paramètres correspondants du composant :
          `train_task = train_evaluate_linear_model_on_iris(hyperparam_name=hp_config_item.name, hyperparam_value=hp_config_item.value)`
        *   KFP gère le passage de `hp_config_item.name` et `hp_config_item.value` aux entrées du composant pour chaque élément de la liste.
    *   Après la boucle, vous pourriez ajouter un composant qui collecte toutes les `model_accuracy` et les `tested_hyperparam_value` pour déterminer la meilleure configuration. 

3.  **Exécution et Observation** :
    *   En exécutant cette pipeline, KFP lancera plusieurs instances du composant `train_evaluate_linear_model_on_iris` en parallèle (ou autant que les ressources le permettent), une pour chaque dictionnaire dans `hyperparams_to_search`.
    *   Chaque instance utilisera une valeur différente pour l'hyperparamètre `C`.
    *   Vous pourrez inspecter les sorties de chaque branche de la boucle pour voir l'accuracy obtenue pour chaque valeur d'hyperparamètre.

Cette approche permet d'explorer efficacement l'espace des hyperparamètres et peut être étendue pour tester plusieurs hyperparamètres en créant une liste d'items plus complexe.

## 4 - Comprendre et configurer le cache des composants

Le cache KFP est une fonctionnalité puissante pour économiser du temps et des ressources en réutilisant les sorties des exécutions précédentes de composants si les entrées et la définition du composant n'ont pas changé. Il est activé par défaut. 

1. Définissez un composant `long_running_task` qui simule un long traitement (par exemple, avec `time.sleep()`).
2. Créez une pipeline `caching_demo_pipeline` avec plusieurs instances de cette tâche.

   - Une tâche avec le cache activé (comportement par défaut).
   - Une autre tâche identique à la première (devrait utiliser le cache).
   - Une troisième tâche avec le cache explicitement désactivé en utilisant task.set_caching_options(enable_caching=False).

3. Exécutez cette pipeline DEUX FOIS sur un backend KFP (pas localement, car le cache local n'est pas supporté de la même manière).

- Lors de la première exécution, toutes les tâches devraient s'exécuter.
- Lors de la deuxième exécution (avec les mêmes paramètres d'entrée pour la pipeline) :
  - La Tâche 1 devrait être récupérée du cache.
  - La Tâche 2 devrait également être récupérée du cache (car identique à la Tâche 1 de la première exécution).
  - La Tâche 3 devrait s'exécuter à nouveau car son cache est désactivé.
- Observez les logs et les icônes de cache dans l'UI KFP.
- Note : Pour tester le cache, il est préférable d'utiliser un backend KFP réel. L'exécution locale avec `DockerRunner` ou `SubprocessRunner` ne simule pas le mécanisme de cache de KFP.

Le cache est une fonctionnalité essentielle pour l'efficacité, mais il faut s'assurer que les composants sont déterministes. Si un composant produit des résultats différents pour les mêmes entrées (par exemple, s'il utilise des nombres aléatoires non initialisés ou lit des données externes changeantes), le cache peut conduire à des résultats incorrects et doit être désactivé.

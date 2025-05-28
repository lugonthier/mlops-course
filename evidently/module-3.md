# Prise en Main d'Evidently : Validation avec les Suites de Tests


Evidently permet de définir des conditions spécifiques (tests) sur les métriques pour obtenir des résultats clairs : Succès (Pass) ou Échec (Fail). Cela aide à automatiser la validation et à maintenir la qualité des modèles en production. Les tests sont généralement exécutés et visualisés au sein d'un `Report`.
                             |

##  Importer les modules nécessaires

Créez un nouveau fichier Python ou un notebook Jupyter et importez les modules suivants :

```python
import pandas as pd
import numpy as np

from sklearn import datasets
from sklearn import ensemble

from evidently import ColumnMapping
from evidently.test_suite import TestSuite

from evidently.tests (
    <TESTS YOU WANT>
)
```

## Utiliser les presets avec Tests auto-générés
Le `ClassificationPreset` peut générer des tests par défaut si `include_tests=True` est spécifié au niveau du `Report`.
```python
    report_with_preset_tests = Report(metrics=[
        ClassificationPreset() 
    ], include_tests=True)
    report_with_preset_tests.run(reference_data=reference_data,
                                 current_data=current_data,
                                 column_mapping=column_mapping)

```

Les conditions des tests auto-générés sont basées sur des heuristiques ou une comparaison avec les données de référence.

## Construire une Suite de Tests Personnalisée avec des Conditions Spécifiques
Définissez un `Report` avec des métriques individuelles, chacune ayant des tests et conditions personnalisés.
```python

test_suite = TestSuite(tests=[
    <TEST_1>,
    ...
    <TEST_2>
  

])

test_suite.run(reference_data=reference_data,
                                current_data=current_data,
                                column_mapping=column_mapping)

```

## Interprétation des Résultats des Tests

Lorsqu'un rapport contenant des tests est généré :
-   **Rapport HTML** : L'onglet "Tests" (ou l'intégration des tests dans les sections de métriques) affichera chaque test avec son statut : `PASS`, `FAIL`, ou `WARNING` .
-   **Sortie JSON** : Le fichier JSON du rapport (`report.json()`) contiendra une section détaillant les résultats de chaque test, y compris la valeur de la métrique et le statut du test.
 
Note: L'exploration du JSON est utile pour l'intégration automatisée des résultats des tests dans des pipelines MLOps.


## 1 - Tests pour la classification

- Ecrire des tests pour la classification du module 1 en vous basant sur des métriques de qualité du modèle ET de qualité des données.
- Afficher et explorer les résultats.


## 2 - Custom Test
Tout comme pour les métriques, Vous pouvez implémenter des tests personnalisés en tant que fonction Python. Le rendu visuel dans le Rapport sera par défaut un simple compteur.

[Voici un notebook](https://github.com/evidentlyai/evidently/blob/ad71e132d59ac3a84fce6cf27bd50b12b10d9137/examples/how_to_questions/how_to_build_metric_over_python_function.ipynb) qui montre comment :
- Comment créer une test personnalisé.
- Comment l'utiliser.

En vous s'inspirant du notebook, à votre tour de créer les tests suivantes à partir de la classification du module 1 :
- [Balanced Accuracy](https://scikit-learn.org/stable/modules/model_evaluation.html#balanced-accuracy-score) supérieur ou égal à 0.7 et strictement inférieur à 0.9
- [F-beta](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.fbeta_score.html#sklearn.metrics.fbeta_score) avec beta = 2, et un score strictement supérieur à 0.6.
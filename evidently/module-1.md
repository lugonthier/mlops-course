# Prise en Main d'Evidently : Évaluation de la Qualité des Modèles

L'objectif de cette partie est de vous familiariser avec Evidently, un outil open-source permettant d'évaluer, de tester et de surveiller les modèles de Machine Learning. Vous apprendrez à utiliser Evidently pour évaluer la qualité des modèles pendant la phase de développement.

## 1 : Introduction à l'Évaluation de Modèles avec Evidently

Evidently aide à comprendre les performances d'un modèle en fournissant des rapports interactifs et détaillés. Il peut être utilisé pour comparer les performances entre différents modèles, ou entre un modèle actuel et une version de référence.

| Concept Clé         | Objectif                                                                                                | Caractéristiques Principales                                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `Report`            | Conteneur principal pour les métriques et les tests. Génère des visualisations HTML interactives.       | Peut inclure plusieurs métriques et presets ; configurable ; exportable en JSON, HTML.                                        |
| `Metrics`           | Mesures spécifiques de la qualité des données ou du modèle (ex: `ClassificationQualityMetric`, `DatasetDriftMetric`). | Unités de base pour l'évaluation ; peuvent être combinées dans des `Report` ou des `TestSuite`.                             |
| `MetricPreset`      | Collections pré-définies de métriques pour des cas d'usage courants (ex: `ClassificationPreset`).       | Simplifie la configuration pour des analyses standard (qualité de classification, dérive des données, qualité de régression). |
| `ColumnMapping`     | Définit le rôle de chaque colonne dans les données (cible, prédiction, caractéristiques numériques/catégorielles). | Essentiel pour qu'Evidently interprète correctement vos données.                                                               |

## 1.1 - Prérequis et Installation

Avant de commencer, assurez-vous d'avoir Python installé. Evidently et les autres bibliothèques nécessaires peuvent être installées via pip.

1.  Créez un nouvel environnement virtuel (recommandé).
2.  Installez les bibliothèques :
    ```bash
    pip -r requirements.txt
    ```

## 1.2 - Importer les modules nécessaires

Créez un nouveau fichier Python ou un notebook Jupyter et importez les modules suivants :

```python
import pandas as pd
import numpy as np

from sklearn import datasets
from sklearn import ensemble

from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import ClassificationPreset, RegressionPreset
from evidently.metrics import <METRICS_YOU_WANT>
```

## 1.3 - Préparation des Données et Entraînement d'un Modèle (Exemple Classification)

Pour illustrer l'évaluation de la qualité d'un modèle de classification, nous utiliserons le jeu de données sur le cancer du sein de scikit-learn.

1.  **Charger les données** : chargez n'importe quel jeu de données de classification binaire et le convertissez le en DataFrame pandas.


1.  **Préparer les jeux de données de référence et actuel** :
    Evidently fonctionne en comparant deux jeux de données : un jeu de "référence" (souvent les données d'entraînement ou un batch précédent) et un jeu "actuel" (par exemple, de nouvelles données ou les données de test).


2.  **Entraîner un modèle simple** :Entraînez un classifier simple. Dans un scénario réel, ce serait votre modèle candidat.


3.  **Générer les prédictions** :
    Ajoutez les prédictions du modèle (probabilités pour la classe positive) aux deux DataFrames.

## 1.4 - Évaluation de la Qualité d'un Modèle de Classification

Maintenant que nos données sont prêtes et que notre modèle a fait des prédictions, nous pouvons utiliser Evidently pour évaluer sa qualité.

1.  **Définir le `ColumnMapping`**:
    Indiquez à Evidently quelles colonnes sont la cible, la prédiction, et les caractéristiques.

    ```python
    column_mapping = ColumnMapping()
    column_mapping.target = TARGET_COLUMN
    column_mapping.prediction = PREDICTION_COLUMN
    # Les caractéristiques numériques et catégorielles sont auto-détectées si non spécifiées.
    # column_mapping.numerical_features = feature_names
    ```

2.  **Utiliser `ClassificationPreset` pour un aperçu rapide** :
    Le `ClassificationPreset` est un ensemble de métriques courantes pour les tâches de classification. Il est idéal pour une première évaluation. Configurez un `Report` avec ce preset :

    ```python
    classification_performance_report = Report(metrics=[
        ClassificationPreset(probas_threshold=0.7), # Vous pouvez spécifier un seuil pour les probabilités
    ])
    ```

3.  **Exécuter et Sauvegarder le Rapport (`ClassificationPreset`)** :
    Exécutez le rapport avec les données de référence, les données actuelles et le `column_mapping`.

    ```python
    classification_performance_report.run(reference_data=<REFERENCE_DATASET>,
                                          current_data=<CURRENT_DATASET>,
                                          column_mapping=column_mapping)

    classification_performance_report.show(mode='inline')
    ```

4.  **Utiliser des métriques de classification spécifiques pour une analyse détaillée** :
    Pour une analyse plus approfondie, vous pouvez configurer un `Report` avec une liste de métriques individuelles.

    ```python
    detailed_classification_report = Report(metrics=<LIST_OF_METRICS>)

   
    detailed_classification_report.run(reference_data=<REFERENCE_DATASET>,
                                    current_data=<CURRENT_DATASET>,
                                     column_mapping=column_mapping)
    
    detailed_classification_report.show(mode='inline')

    ```

## 1.5 - Préparation des Données et Entraînement d'un Modèle (Exemple Régression)

Nous allons maintenant passer à un exemple de régression en utilisant le jeu de données "California Housing".
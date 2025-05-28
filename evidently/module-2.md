# Créer une métrique personnalisé (Custom Metric)

Vous pouvez implémenter toute métrique personnalisé en tant que fonction Python. Le rendu visuel dans le Rapport sera par défaut un simple compteur.

[Voici un notebook](https://github.com/evidentlyai/evidently/blob/ad71e132d59ac3a84fce6cf27bd50b12b10d9137/examples/how_to_questions/how_to_build_metric_over_python_function.ipynb) qui montre comment :
- Comment créer une métrique personnalisé.
- Comment l'utiliser.


# 1 - Métrique Personnalisé pour la Regression

En vous s'inspirant du notebook, à votre tour de créer les métriques suivantes à partir de la regression du module 1 :
- [Score de Variance Expliquée (Explained Variance Score)](https://scikit-learn.org/stable/modules/model_evaluation.html#explained-variance-score)
- [Erreur Maximale (Max Error)](https://scikit-learn.org/stable/modules/model_evaluation.html#max-error)
# Cas d'Usage Industriel - Promotion d'un Modèle de Churn
**Objectif :** Simuler un flux de travail réaliste pour la promotion d'un modèle de prédiction de churn (attrition client) en utilisant le MLflow Model Registry et le concept d'alias.

Nous nous basons sur le modèle de churn entraîné dans les exercices précédents (ou supposons que plusieurs versions ont été entraînées et loguées via mlflow run). Nous allons simuler le processus de validation et de promotion d'une nouvelle version vers un environnement de "production".


## 1 - Identifier et Enregistrer le Meilleur Modèle


- Utilisez l'UI MLflow ou l'API `MlflowClient().search_runs()` pour identifier le run ayant produit la meilleure version du modèle de churn (basé sur une métrique clé comme F1-score ou AUC, enregistrée précédemment). Notez le `run_id` de ce run.
- Si ce n'est pas déjà fait lors du `log_model`, enregistrez ce modèle dans le registre. Choisissez un nom unique et descriptif, par exemple ChurnPredictor. Utilisez l'API `mlflow.register_model()` (ou avec le client `client.create_registered_model`).

Note : Si le modèle "ChurnPredictor" existe déjà, cela créera une nouvelle version.

## 2 - Alias et Tags Initiaux (Simulation Post-Entraînement)

- Utilisez `MlflowClient` pour interagir avec le registre.
- Assignez un alias initial à cette nouvelle version, par exemple "candidate-latest" ou "staging-candidate", indiquant qu'elle est prête pour validation.
- Ajoutez des tags pertinents pour indiquer son statut et le contexte. (`set_model_version_tag`)

## 3 - Validation

Imaginez qu'une série de tests automatisés (vérification de performance sur un jeu de données de validation, tests d'équité, etc.) sont exécutés sur le modèle chargé via l'alias `"staging-candidate"`.

Si les tests réussissent, mettez à jour le tag de validation.


## 4 - Promouvoir en "Production" (Mise à Jour de l'Alias)

- Supposons qu'une version antérieure (par exemple, `old_version = new_version - 1`, si elle existe) détient actuellement l'alias `"production-live"`.
- Le moment clé : réassignez l'alias `"production-live"` à la nouvelle version validée (`new_version`). L'ancienne version perdra cet alias (un alias ne pointe que vers une seule version à la fois pour un modèle donné).

Note : La suppression explicite de l'alias de l'ancienne version n'est généralement pas nécessaire car `set_registered_model_alias` le déplace. La fonction `delete_registered_model_alias` existe si besoin.


## 5 - Charger le Modèle de Production pour Inférence

Démontrez comment une application ou un service chargerait le modèle en utilisant uniquement l'alias "production-live", sans connaître le numéro de version spécifique


## 6 - Effectuer une Inférence

- Préparez quelques données d'exemple au format attendu par le modèle.
- Utilisez le modèle chargé pour faire des prédictions de churn.


## 7 - Vérification dans la UI MLflow

- Retournez à l'UI MLflow.
- Naviguez vers la page "Models".
- Trouvez le modèle enregistré "ChurnPredictor".
- Montrez que l'alias "production-live" pointe maintenant vers la new_version.
- Montrez que l'alias "staging-candidate" pointe toujours vers new_version (un modèle peut avoir plusieurs alias). Vous pourriez vouloir le supprimer ou le réassigner dans un vrai workflow.
- Montrez les tags mis à jour sur la new_version (validation_status: passed).
- Si applicable, montrez le tag d'archivage sur l'old_version.
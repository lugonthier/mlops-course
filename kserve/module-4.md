# Module 4 : Intégration du déploiement KServe dans les pipelines Kubeflow (KFP)

Ce module décrit comment incorporer le déploiement de modèles KServe dans vos pipelines Kubeflow (KFP) existantes.

L'objectif principal est d'automatiser le déploiement des modèles en ajoutant une nouvelle étape à votre pipeline d'entraînement KFP actuelle.

## Lignes directrices

Pour intégrer le déploiement KServe :

1.  **S'appuyer sur le Module 3 :** Utilisez le script Python et la logique du `KServeClient` développés dans le Module 3 (SDK KServe) comme base pour votre mécanisme de déploiement.

2.  **Créer un composant KFP :** Encapsulez la logique de déploiement du SDK KServe dans un composant Kubeflow Pipelines dédié. Ce composant gérera la création ou la mise à jour de l'`InferenceService` pour votre modèle entraîné.

3.  **Mettre à jour votre pipeline d'entraînement :** Intégrez ce nouveau composant KFP dans votre pipeline d'entraînement existante. Cette étape s'exécute généralement après que votre modèle a été entraîné et validé avec succès. Son exécution peut être conditionnée par l'atteinte de seuils de performance par le modèle, et elle peut être suivie d'autres étapes (par exemple, tests A/B, notifications, etc.). Le composant utilisera la `storageUri` du modèle (ou d'autres sorties nécessaires des étapes précédentes) comme entrée.

En suivant ces étapes, vous pouvez étendre de manière transparente votre pipeline d'entraînement pour déployer automatiquement des modèles à l'aide de KServe.
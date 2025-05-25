| Commande | Description Principale | Lien MLOps |
|----------|------------------------|------------|
| dvc init | Initialise DVC dans un dépôt Git existant. | Mise en place initiale de l'environnement versionné. |
| dvc add <cible> | Commence à suivre un fichier ou dossier avec DVC, le déplace/lie au cache et crée le fichier .dvc. | Versionnement des données et modèles. |
| dvc remote add... | Configure un stockage distant (cloud, local, SSH...). | Collaboration, sauvegarde, partage de données/modèles. |
| dvc push [-r <remote>] | Téléverse les données/modèles du cache local vers le stockage distant. | Partage des artefacts, sauvegarde. |
| dvc pull [-r <remote>] | Télécharge les données/modèles depuis le stockage distant vers le cache local et l'espace de travail. | Récupération des artefacts par les collaborateurs ou les systèmes CI/CD. |
| dvc checkout [<cibles>] | Synchronise les fichiers de l'espace de travail avec les versions pointées par les fichiers .dvc actuels (via Git). | Navigation entre les versions de données/modèles. |
| dvc stage add... | Définit une étape de pipeline dans dvc.yaml (commande, dépendances, sorties, paramètres...). | Définition de workflows ML automatisés et reproductibles. |
| dvc repro [<étapes>] | Exécute les étapes nécessaires du pipeline défini dans dvc.yaml, met à jour dvc.lock. | Automatisation de l'exécution du workflow, reproductibilité. |
| dvc status | Affiche les différences entre l'espace de travail, le cache DVC, et l'état enregistré (.dvc, dvc.lock). | Vérification de la cohérence du projet. |
| dvc metrics show/diff | Affiche ou compare les métriques définies dans dvc.yaml entre différentes versions/expériences. | Suivi et évaluation des performances des modèles. |
| dvc plots show/diff | Génère et/ou compare des visualisations (plots) définies dans dvc.yaml entre différentes versions/expériences. | Analyse visuelle des performances et des résultats. |
| dvc exp run/show/diff | Lance, liste ou compare des expériences ML gérées par DVC (variations de code/paramètres). | Gestion structurée des expérimentations. |

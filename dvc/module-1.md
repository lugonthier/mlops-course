# Module 1 : Initialiser DVC et Versionner des Données

Passons maintenant à la pratique. Nous allons initialiser DVC dans un projet Git existant et commencer à versionner un fichier de données.

Prérequis :
- Un projet avec Git déjà initialisé (`git init`).
- DVC installé (voir [la documentation DVC](https://dvc.org/doc/install) pour l'installation).
- Un fichier de données (par exemple, data.csv) dans votre projet.


## 1. Initialiser DVC

Ouvrez votre terminal à la racine de votre projet Git et exécutez :
```bash
dvc init
```

Cette commande crée la structure interne de DVC (le répertoire `.dvc`) et configure le projet pour utiliser DVC. Elle crée également des fichiers à ajouter à Git (`.dvc/config`, `.dvc/.gitignore`).

## 2.  Vérifier et Commiter l'Initialisation DVC
Vérifiez les fichiers créés par DVC avec `git status` :
```bash
git status
```
Vous devriez voir les nouveaux fichiers dans le répertoire `.dvc`. 
Ajoutez-les à Git et commitez :
```bash
git add .dvc/.gitignore .dvc/config
git commit -m "Initialize DVC"
```

Votre projet est maintenant prêt à versionner des données avec DVC.


## 3. Ajouter un Fichier de Données au Suivi DVC
Supposons que vous ayez un fichier `data.csv` dans un dossier `data/`. Pour le placer sous le contrôle de version de DVC, exécutez :
```bash
dvc add data/data.csv
```
DVC va maintenant :

- Calculer le hash MD5 du fichier `data.csv`.
- Créer le fichier de métadonnées `data/data.csv.dvc` contenant ce hash et d'autres informations.
- Déplacer (ou lier) le fichier `data.csv` original vers le cache DVC (`.dvc/cache`).
- Ajouter `data/data.csv` au fichier `.gitignore` approprié (soit à la racine, soit dans `data/.gitignore`) pour que Git l'ignore.



## 4. Commiter le Fichier .dvc avec Git
Le fichier `data.csv` lui-même est maintenant ignoré par Git, mais le fichier `data/data.csv.dvc` (qui est petit) doit être versionné par Git pour enregistrer cette version des données. Vérifiez avec `git status` :
```bash
git status
```
Vous devriez voir `data/data.csv.dvc` et le `.gitignore` modifié. Ajoutez-les et commitez :
```bash
git add data/data.csv.dvc data/.gitignore
git commit -m "Add raw data data.csv"
```

## 5. Ajouter un Dossier de Données
Si vous avez un dossier contenant plusieurs fichiers (par exemple, `data/images/`), vous pouvez l'ajouter de la même manière :
```bash
dvc add data/images
```
DVC créera un seul fichier `data/images.dvc` pour suivre l'ensemble du dossier et ajoutera `data/images/` au `.gitignore.` N'oubliez pas de commiter le fichier `data/images.dvc` et le `.gitignore` avec Git.

À ce stade, vous avez versionné votre première donnée avec DVC et enregistré sa référence dans Git. Le fichier original est stocké de manière sécurisée et efficace dans le cache DVC.
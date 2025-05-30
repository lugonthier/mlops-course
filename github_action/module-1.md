# Pratique : Créer Votre Premier Workflow CI Python avec GitHub Actions

Ce guide vous expliquera comment créer un workflow d'Intégration Continue (CI) pour un projet Python. L'objectif est de reproduire la fonctionnalité de `module-1-ci.yaml` en comprenant chaque étape de sa construction.

## Prérequis

Assurez-vous d'avoir la structure de projet suivante. Pour cet exercice pratique, les fichiers Python (`app.py`, `test_app.py`) et le fichier `requirements.txt` dans le dossier `github_action/module_1/` vous sont déjà fournis. Votre tâche est de créer le fichier YAML du workflow.

```
votre-repo/
├── .github/
│   └── workflows/  // C'est ici que vous créerez votre fichier YAML de CI
├── github_action/
│   └── module_1/
│       ├── app.py         // Fourni
│       ├── test_app.py      // Fourni
│       └── requirements.txt // Fourni
└── ... (autres fichiers)
```

Le dossier `github_action/module_1/` contient votre application Python, les tests, et un fichier `requirements.txt`.

## Étapes pour Créer `module-1-ci.yaml`

### 1. Créer le Fichier de Workflow

Dans votre dépôt, naviguez vers le dossier `.github/workflows/`. Créez-y un nouveau fichier que vous nommerez `module-1-ci.yaml` (ou le nom de votre choix, mais nous utiliserons celui-ci pour la suite du guide).

### 2. Nommer Votre Workflow

Au début de votre fichier `module-1-ci.yaml`, la première chose à définir est le nom de votre workflow. Utilisez la clé `name` pour cela. Ce nom sera visible dans l'onglet "Actions" de votre dépôt GitHub. Choisissez un nom descriptif, par exemple "Python CI".

### 3. Définir les Déclencheurs

Ensuite, spécifiez les événements qui déclencheront l'exécution de ce workflow. Utilisez la clé `on`. Pour une intégration continue classique, configurez le workflow pour qu'il se lance à chaque `push` vers le dépôt, ainsi que pour chaque `pull_request`.

### 4. Définir les Tâches (Jobs)

Un workflow est composé d'une ou plusieurs tâches (jobs). Définissez une section `jobs` dans votre fichier. Pour cette pratique, nous aurons une seule tâche. Nommez cette tâche `build`.

### 5. Spécifier l'Exécuteur (Runner) et le Conteneur

Pour la tâche `build` que vous venez de définir, vous devez spécifier son environnement d'exécution.
- Indiquez que la tâche doit s'exécuter sur la dernière version d'Ubuntu en utilisant la clé `runs-on`.
- Précisez que les étapes de cette tâche s'exécuteront à l'intérieur d'un conteneur Docker. Utilisez la clé `container` et sa sous-clé `image` pour spécifier l'image `python:3.10-slim`. Cela garantit un environnement Python 3.10 cohérent.

### 6. Ajouter des Étapes à la Tâche `build`

À l'intérieur de la tâche `build`, définissez une liste d'étapes (steps). Chaque étape exécute une commande ou une action.

#### Étape 6.1 : Récupérer le Code (Check Out Code)

La première étape cruciale est de permettre au workflow d'accéder au code de votre dépôt. Donnez un nom à cette étape (par exemple, "Check out code"). Utilisez l'action `actions/checkout@v4` fournie par GitHub pour cela, en utilisant la clé `uses`.

#### Étape 6.2 : Installer les Dépendances

Créez une nouvelle étape pour installer les dépendances Python.
- Nommez cette étape (par exemple, "Install dependencies").
- Spécifiez le répertoire de travail avec `working-directory` pour que les commandes s'exécutent dans `github_action/module_1`, là où se trouve `requirements.txt`.
- Utilisez la clé `run` pour exécuter des commandes shell. Vous aurez besoin de deux commandes : la première pour mettre à jour `pip` (`python -m pip install --upgrade pip`) et la seconde pour installer les paquets depuis `requirements.txt` (`pip install -r requirements.txt`).

#### Étape 6.3 : Analyse Statique avec flake8 (Lint with flake8)

Ajoutez une étape pour l'analyse statique du code avec `flake8`.
- Nommez cette étape (par exemple, "Lint with flake8").
- Définissez le `working-directory` sur `github_action/module_1`.
- Dans la section `run`, vous inclurez les commandes multi-lignes suivantes. Utilisez `|` après `run:` pour cela.

```bash
# Arrête la construction s'il y a des erreurs de syntaxe Python ou des noms non définis
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
# exit-zero traite toutes les erreurs comme des avertissements. L'éditeur GitHub a une largeur de 127 caractères
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

Explication des commandes `flake8` :
    1.  `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`: Cette commande vérifie le répertoire courant (`.`) pour des erreurs spécifiques.
        *   `--count`: Affiche le nombre total d'erreurs et d'avertissements.
        *   `--select=E9,F63,F7,F82`: Se concentre sur les erreurs de syntaxe (`E9`), les erreurs de formatage de f-string (`F63`), les erreurs d'importation (`F7`), et les erreurs de nom non défini (`F82`). Ce sont généralement des erreurs bloquantes.
        *   `--show-source`: Montre la ligne de code source qui a causé l'erreur.
        *   `--statistics`: Affiche des statistiques sur les types d'erreurs trouvées.
        Si cette commande trouve des erreurs, elle retournera un code de sortie non nul, ce qui fera échouer l'étape et donc le workflow.
    2.  `flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics`: Cette commande effectue une analyse plus large.
        *   `--exit-zero`: Assure que `flake8` se termine avec un code de sortie 0 même si des problèmes sont trouvés. Cela signifie que ces problèmes seront traités comme des avertissements et ne feront pas échouer la construction.
        *   `--max-complexity=10`: Vérifie la complexité cyclomatique des fonctions (une mesure de la complexité du code).
        *   `--max-line-length=127`: Vérifie que les lignes ne dépassent pas 127 caractères.

#### Étape 6.4 : Tester avec pytest

La dernière étape consiste à exécuter les tests avec `pytest`.
- Nommez cette étape (par exemple, "Test with pytest").
- Spécifiez le `working-directory` : `github_action/module_1`.
- Utilisez `run` pour exécuter la commande suivante :

```bash
pytest
```

Explication de la commande `pytest` :
    *   `pytest`: Lance simplement l'outil de test `pytest`. `pytest` découvrira et exécutera automatiquement les tests dans le répertoire courant (et ses sous-répertoires) en suivant ses conventions de nommage (fichiers `test_*.py` ou `*_test.py`, fonctions `test_*`). Si un test échoue, `pytest` retournera un code de sortie non nul, ce qui fera échouer l'étape.

### 7. Vérification du Fichier de Workflow Final

Une fois toutes ces étapes configurées dans votre fichier `.github/workflows/module-1-ci.yaml`, vous aurez un workflow CI complet. Comparez mentalement votre structure avec celle du fichier `module-1-ci.yaml` original si vous y avez accès, pour vous assurer que vous avez couvert tous les aspects nécessaires.


# Pratique : Utiliser une Matrice de Stratégie avec GitHub Actions

Ce guide vous expliquera comment utiliser une matrice de stratégie dans un workflow d'Intégration Continue (CI) pour un projet Python, afin d'exécuter vos tâches sur plusieurs versions de Python. L'objectif est de comprendre comment modifier un workflow existant (comme celui de `module-1-ci.yaml`) pour y intégrer une matrice, en s'inspirant de `module-2-ci.yaml`.

## Prérequis

La structure de projet reste la même que pour le module 1. Nous allons nous concentrer sur la modification du fichier YAML du workflow pour y introduire une matrice de versions Python.

```
votre-repo/
├── .github/
│   └── workflows/  // C'est ici que vous créerez ou modifierez votre fichier YAML
├── github_action/
│   └── module_1/   // Le code de l'application reste le même
│       ├── app.py
│       ├── test_app.py
│       └── requirements.txt
└── ... (autres fichiers)
```

## Objectif

L'objectif est de créer un workflow nommé `module-2-ci.yaml` (ou de modifier votre workflow existant) pour qu'il exécute les étapes de construction, de linting et de test sur plusieurs versions de Python (par exemple, 3.9, 3.10, 3.11, et 3.12).

## Étapes pour Intégrer une Matrice
Pour cet exercice, partez de votre fichier `module-1-ci.yaml`. Vous pouvez le dupliquer et le renommer en `module-2-ci.yaml` si vous souhaitez conserver l'original. Les configurations initiales telles que le nom du workflow (`name`) et les déclencheurs (`on:`) peuvent être conservées telles quelles ou ajustées au besoin.

L'accent sera mis sur la modification de la tâche `build` pour y introduire une matrice de stratégie.

### 1. Définir la Matrice de Stratégie dans la Tâche `build`

Commencez par votre fichier `module-1-ci.yaml`. Vous pouvez le dupliquer et le renommer `module-2-ci.yaml` pour cet exercice. Les sections `name` et `on` (déclencheurs) peuvent rester identiques.

```yaml
on: [push, pull_request]
```

### 2. Spécifier l'Exécuteur (Runner) et le Conteneur Dynamique

Modifiez la spécification du conteneur pour qu'il utilise la version de Python définie dans la matrice. Vous pouvez accéder à la valeur de la variable de matrice `python-version` avec la syntaxe `${{ matrix.python-version }}`.

Cela signifie que pour chaque valeur dans `matrix.python-version`, une nouvelle instance de la tâche `build` sera lancée avec l'image Docker Python correspondante (par exemple, `python:3.9-slim`, `python:3.10-slim`, etc.).

### 3. Adapter les Étapes à la Matrice

Les étapes de la tâche `build` restent similaires, mais vous pouvez utiliser la variable de matrice dans les noms des étapes pour une meilleure lisibilité dans les logs de GitHub Actions.

#### Étape 3.1 : Récupérer le Code (Check Out Code)

Cette étape ne change pas.

```yaml
    steps:
      - name: Check out code
        uses: actions/checkout@v4
```

#### Étape 3.2 : Installer les Dépendances

Le nom de l'étape peut être dynamisé pour inclure la version de Python. Les commandes exécutées restent les mêmes, mais elles s'exécuteront avec la version de Python du conteneur actuel.

```yaml
      - name: Install dependencies for Python ${{ matrix.python-version }}
        working-directory: github_action/module_1
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
```

#### Étape 3.3 : Analyse Statique avec flake8

Le nom de l'étape peut également être dynamisé. Notez que dans l'exemple `module-2-ci.yaml`, une seule commande `flake8` est utilisée, avec `--exit-zero` pour ne pas faire échouer le build sur des problèmes de style. Ceci est une configuration courante lorsque l'on teste sur plusieurs environnements, où l'on veut collecter tous les résultats sans qu'un échec bloque les autres.

```yaml
      - name: Lint with flake8 for Python ${{ matrix.python-version }}
        working-directory: github_action/module_1
        run: |
          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```
Si vous souhaitez conserver le comportement strict de `module-1-ci.yaml` (faire échouer le workflow sur certaines erreurs `flake8`), vous pouvez réintroduire la première commande `flake8` plus stricte ici. Cependant, pour une matrice, il est souvent préférable de laisser tous les tests s'exécuter.

#### Étape 3.4 : Tester avec pytest

De même, dynamisez le nom de l'étape. La commande `pytest` s'exécutera avec la version de Python correspondante.

```yaml
      - name: Test with pytest for Python ${{ matrix.python-version }}
        working-directory: github_action/module_1
        run: |
          pytest
```


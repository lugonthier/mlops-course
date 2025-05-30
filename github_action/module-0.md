# Installer et Utiliser `act` pour Exécuter des GitHub Actions Localement

`act` est un outil en ligne de commande qui vous permet d'exécuter vos GitHub Actions localement. C'est très utile pour tester vos workflows sans avoir à les pousser sur GitHub à chaque modification. `act` utilise Docker pour exécuter les jobs définis dans vos workflows.

## Prérequis

Avant d'installer `act`, vous devez avoir Docker d'installé et en cours d'exécution sur votre système.
- **macOS**: Installez [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/).
- **Windows**: Installez [Docker Desktop on Windows](https://docs.docker.com/desktop/install/windows-install/).
- **Linux**: Installez [Docker Engine](https://docs.docker.com/engine/install/).

## Méthodes d'Installation Principales

Il existe plusieurs façons d'installer `act`. Voici les plus courantes :

### 1. Via Homebrew (macOS et Linux)

Si vous utilisez macOS ou Linux et que Homebrew est installé, vous pouvez installer `act` avec la commande suivante :

```bash
brew install act
```

### 2. Via le script Bash (Linux et macOS)

Vous pouvez installer une version pré-compilée de `act` sur n'importe quel système disposant de `bash` avec la commande suivante :

```bash
curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```
Notez que ce script installe la dernière version stable.

### Autres Méthodes d'Installation

`act` est également disponible via d'autres gestionnaires de paquets comme Chocolatey (Windows), Scoop (Windows), Nix/NixOS, et plus encore. Vous pouvez également télécharger les binaires pré-compilés manuellement ou compiler depuis les sources.

Pour une liste complète des méthodes d'installation et des instructions détaillées, veuillez consulter la documentation officielle : [@https://nektosact.com/installation/index.html](https://nektosact.com/installation/index.html).

## Tester une GitHub Action avec `act`

Une fois `act` installé, vous pouvez tester vos workflows GitHub Actions.

1.  **Créez un fichier de workflow simple.**
    Par exemple, créez un fichier `.github/workflows/main.yml` dans votre projet avec le contenu suivant :

    ```yaml
    name: CI Simple
    on: [push]
    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
        - uses: actions/checkout@v3
        - name: Run a one-line script
          run: echo "Bonjour le monde depuis act !"
    ```

2.  **Exécutez `act`**
    Naviguez jusqu'au répertoire racine de votre projet dans votre terminal et exécutez la commande `act` :

    ```bash
    act
    ```

    Par défaut, `act` exécutera l'événement `push`. Si vous souhaitez déclencher un événement spécifique, vous pouvez le spécifier :

    ```bash
    act pull_request
    ```

    La première fois que vous exécutez `act`, il vous demandera quelle image Docker utiliser pour les runners (par exemple, `Micro` ou `Medium`). Choisissez celle qui convient le mieux à vos besoins. `Medium` est un bon point de départ.

    Vous devriez voir la sortie de votre workflow, y compris le message "Bonjour le monde depuis act!".


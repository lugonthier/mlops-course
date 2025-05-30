# Pratique 3 : Workflow Réutilisable avec Entrées et Secrets (Test Local avec `act`)

cette pratique expliquera comment créer un workflow réutilisable qui accepte des entrées (`inputs`) et des secrets (`secrets`), puis comment l'appeler depuis un autre workflow.

### 1. Créer le Workflow Réutilisable (`reusable-echo.yml`)

Ce workflow sera conçu pour être appelé par d'autres. Il affichera un message fourni en entrée et confirmera la présence d'un secret.

   a. **Création du Fichier :**
      Dans votre répertoire `reusable-workflow-act`, créez la structure de dossiers `.github/workflows/`.
      À l'intérieur de `.github/workflows/`, créez un fichier nommé `reusable-echo.yml`.

   b. **Nom et Déclencheur `workflow_call` :**
      - Au début de votre fichier, donnez un nom à votre workflow (par exemple, `Reusable Echo Workflow`) en utilisant la clé `name`.
      - Configurez-le pour être réutilisable en utilisant `on: workflow_call:`.

   c. **Définir les Entrées (`inputs`) :**
      Sous `workflow_call:`, ajoutez une section `inputs:`.
      - Définissez une entrée nommée `message`.
        - Ajoutez une `description:` (par exemple, 'Message to echo').
        - Rendez-la obligatoire en utilisant `required: true`.
        - Spécifiez son type avec `type: string`.

   d. **Définir les Secrets Attendus (`secrets`) :**
      Toujours sous `workflow_call:`, ajoutez une section `secrets:`.
      - Définissez un secret attendu nommé `MY_TOKEN`.
        - Ajoutez une `description:` (par exemple, 'A token to demonstrate secret passing').
        - Rendez-le obligatoire avec `required: true`.

   e. **Configurer la Tâche (`jobs`) et ses Étapes (`steps`) :**
      - Définissez une section `jobs:`.
      - À l'intérieur, créez une tâche unique (par exemple, `echo-message`).
        - Spécifiez qu'elle doit s'exécuter sur `ubuntu-latest` avec `runs-on: ubuntu-latest`.
      - Dans cette tâche, définissez les `steps:` :
        - **Première étape :** Nommez-la (par exemple, `Echo the input message`).
          Utilisez `run:` pour exécuter une commande qui affiche la valeur de l'entrée `message`. Vous pouvez accéder à cette valeur avec la syntaxe `${{ inputs.message }}`.
        - **Deuxième étape :** Nommez-la (par exemple, `Check for secret presence`).
          Utilisez `run:` pour exécuter une commande qui affiche la présence du secret `MY_TOKEN` sans révéler sa valeur.
          Pour cela, vous pouvez définir une variable d'environnement dans l'étape en utilisant `env:` :
          `SECRET_STATUS: ${{ secrets.MY_TOKEN && 'TOKEN_PRESENT_AND_NOT_EMPTY' || 'TOKEN_MISSING_OR_EMPTY' }}`
          Ensuite, affichez la valeur de cette variable d'environnement (`echo "Secret status: $SECRET_STATUS"`).

### 2. Créer le Workflow Appelant (`caller.yml`)

Ce workflow servira à déclencher et à tester le workflow réutilisable.

   a. **Création du Fichier :**
      Dans le même répertoire `.github/workflows/`, créez un fichier nommé `caller.yml`.

   b. **Nom et Déclencheur :**
      - Donnez un nom à ce workflow (par exemple, `Caller Workflow`) avec la clé `name`.
      - Définissez un déclencheur. Pour des tests locaux faciles avec `act`, `on: workflow_dispatch` est une bonne option, ou utilisez `on: [push]`.

   c. **Configurer la Tâche d'Appel (`jobs`) :**
      - Définissez une section `jobs:`.
      - Créez une tâche unique (par exemple, `call-reusable-workflow`).
        - Pour appeler le workflow réutilisable localement, utilisez la clé `uses:` pointant vers le chemin relatif du fichier : `uses: ./.github/workflows/reusable-echo.yml`.
        - **Passer les Entrées (`with`) :** Utilisez la clé `with:` pour fournir les valeurs des entrées attendues par `reusable-echo.yml`.
          Fournissez une valeur pour l'entrée `message` (par exemple, `message: "Hello from the Caller Workflow!"`).
        - **Passer les Secrets (`secrets`) :** Utilisez la clé `secrets:` pour transmettre les secrets.
          Le workflow réutilisable attend `MY_TOKEN`. Le workflow appelant doit fournir ce secret. Vous pouvez le faire en passant un secret que le workflow appelant reçoit lui-même. Pour `act`, ce secret source sera fourni via un fichier `.secrets` ou en ligne de commande.
          Dans `caller.yml`, mappez-le comme ceci : `MY_TOKEN: ${{ secrets.PASSED_TOKEN }}`. `PASSED_TOKEN` est le nom du secret que `act` fournira à `caller.yml`.

### 3. Préparer les Secrets pour `act`

Pour que `act` puisse simuler la présence de secrets, vous devez les lui fournir.

   a. **Créer le Fichier `.secrets` (Méthode Recommandée) :**
      À la racine de votre projet `reusable-workflow-act` (au même niveau que le dossier `.github`), créez un fichier nommé `.secrets`.
      Dans ce fichier, définissez le secret `PASSED_TOKEN` que votre `caller.yml` s'attend à recevoir. Ajoutez une ligne avec le nom du secret et sa valeur :
      `PASSED_TOKEN=MaSuperValeurSecretePourLesTestsLocaux`
      (Remplacez la valeur par celle de votre choix).

   b. **Alternative : Ligne de Commande (Moins Recommandé pour les secrets fréquents) :**
      Vous pouvez aussi passer les secrets directement à `act` lors de son exécution via l'option `--secret NOM_DU_SECRET=valeur`.

### 4. Exécuter et Vérifier avec `act`

Une fois les deux fichiers de workflow et, si vous utilisez cette méthode, le fichier `.secrets` en place, vous pouvez tester.

   a. **Lancer `act` :**
      Ouvrez votre terminal et naviguez à la racine de votre projet `reusable-workflow-act`.
      - Si vous avez utilisé `on: [push]` (et que vous avez commité vos fichiers) ou si `act` prend le premier workflow par défaut :
        ```bash
        act --secret-file .secrets
        ```
      - Si vous avez utilisé `on: workflow_dispatch` pour `caller.yml` :
        ```bash
        act workflow_dispatch --secret-file .secrets
        ```
      - Si vous passez le secret en ligne de commande (adaptez selon le déclencheur) :
        ```bash
        act --secret PASSED_TOKEN=MaSuperValeurSecretePourLesTestsLocaux
        ```

   b. **Analyser la Sortie :**
      Dans les logs produits par `act`, vous devriez observer :
      - L'exécution du workflow `Caller Workflow`.
      - L'appel et l'exécution subséquente du `Reusable Echo Workflow`.
      - Dans les étapes de `Reusable Echo Workflow` :
        - Le message que vous avez passé depuis `caller.yml` (par exemple, "Input message: Hello from the Caller Workflow!").
        - Une indication que le secret `MY_TOKEN` était présent et non vide (par exemple, "Secret status: TOKEN_PRESENT_AND_NOT_EMPTY").





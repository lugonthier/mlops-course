# Module 6 : Collaborer Efficacement avec DVC et Git
## Scénario de Collaboration Simple

Illustrons comment deux collaborateurs, Alice et Bob, peuvent travailler ensemble sur un projet utilisant DVC et Git, en partageant le code via un dépôt Git distant (comme GitHub) et les données/modèles via un remote DVC partagé (comme un bucket S3 ou même un dossier local partagé accessible par les deux).

**Scénario :** Alice initialise un projet, ajoute des données et un pipeline. Bob clone le projet, récupère les données, modifie le pipeline, et Alice intègre les changements de Bob.

**Prérequis :**
- Un dépôt Git distant (ex: sur GitHub, GitLab).
Alice et Bob ont Git et DVC installés et configurés.
- Un emplacement de stockage distant DVC accessible par Alice et Bob (ex: un bucket S3 configuré, ou pour simplifier cet exemple, un dossier local partagé `/mnt/shared/dvc-storage`).


## 1 - Mise en Place Initiale (Alice)

Alice crée un nouveau dossier, initialise Git et DVC :
```bash
mkdir projet-mlops-dvc
cd projet-mlops-dvc
git init
dvc init
git add.dvc/config.dvc/.gitignore
git commit -m "Initialize DVC"
```

Alice ajoute un fichier de données (ex: `data/input.csv`) et le versionne :
```bash
mkdir data
echo "col1,col2\n1,a\n2,b" > data/input.csv
dvc add data/input.csv
git add data/input.csv.dvc data/.gitignore
git commit -m "Add initial data"
```

Alice crée un script simple `src/process.py` et définit une étape de pipeline :
```bash
mkdir src
echo "print('Processing data...')" > src/process.py # Script factice
dvc stage add -n process -d src/process.py -d data/input.csv -o data/output.txt python src/process.py
git add src/process.py dvc.yaml data/.gitignore # Ajouter le nouveau.gitignore pour data/output.txt
git commit -m "Add process stage"
```

Alice configure le remote DVC partagé (en supposant que `/mnt/shared/dvc-storage` existe et est accessible) :
```bash
dvc remote add shared-storage /mnt/shared/dvc-storage
# Important: Commiter la configuration du remote
git add.dvc/config
git commit -m "Configure shared DVC remote"
```

Alice configure le remote Git et pousse le code :
```bash
git remote add origin <url_du_depot_git_distant>
git push -u origin main
```

Alice pousse les données vers le remote DVC partagé :
```bash
dvc push -r shared-storage
```


## 2 - Récupération du Projet (Bob)

Bob clone le dépôt Git :
```bash
git clone <url_du_depot_git_distant> projet-bob
cd projet-bob
```

Bob a maintenant le code, `dvc.yaml`, `.dvc` files, et la configuration du remote DVC partagé.
Bob récupère les données depuis le remote DVC :
```bash
dvc pull -r shared-storage
```
Le fichier `data/input.csv` apparaît dans son workspace.
Bob peut exécuter le pipeline (qui devrait être à jour initialement) :
```bash
dvc repro
# Le fichier data/output.txt est généré
```




## 3 Modification par Bob

Bob crée une branche pour ses modifications :
```bash
git checkout -b feature/update-processing
```

Bob modifie le script `src/process.py` (par exemple, change le message imprimé).
Bob exécute le pipeline. `dvc repro` détecte le changement dans `src/process.py` (qui est une dépendance de l'étape process) et ré-exécute l'étape :
```bash
dvc repro
# L'étape 'process' est ré-exécutée, data/output.txt est mis à jour
# dvc.lock est mis à jour
```

Bob commite ses changements (le script modifié et le `dvc.lock` mis à jour) :
```bash
git add src/process.py dvc.lock
git commit -m "Update processing logic"
```

Bob pousse sa branche Git :
```bash
git push origin feature/update-processing
```

Bob pousse les données potentiellement modifiées (ici, `data/output.txt`) vers le remote DVC. Même si le contenu n'a pas changé, le hash de l'étape dans `dvc.lock` a changé, il est bon de pousser pour assurer la cohérence si la sortie avait changé.
```bash
dvc push -r shared-storage
```




## 4 - Revue et Fusion (Alice)

Alice voit la nouvelle branche ou la Pull Request de Bob sur GitHub/GitLab.
Alice fetch les changements et checkoute la branche de Bob :
```bash
git fetch origin
git checkout feature/update-processing
```

Alice récupère les données associées à cette branche (si des sorties suivies par DVC ont changé et ont été poussées par Bob) :
```bash
dvc pull -r shared-storage
```

Alice examine le code (`src/process.py`) et les changements dans `dvc.lock`. Elle peut exécuter dvc repro pour vérifier que tout fonctionne.
Si tout est OK, Alice retourne sur la branche principale et merge la branche de Bob :
```bash
git checkout main
git merge feature/update-processing
```

Alice résout les éventuels conflits Git (par exemple, si elle avait aussi modifié `dvc.lock` sur main).
Alice pousse la branche principale mise à jour sur Git :

```bash
git push origin main
```

Alice peut faire un dernier `dvc push -r shared-storage` pour s'assurer que toutes les données finales associées à main sont sur le remote DVC.


Ce scénario illustre le flux de travail collaboratif typique : utiliser Git pour le code et les métadonnées DVC (`.dvc`, `dvc.yaml`, `dvc.lock`, `params.yaml`), et DVC (push/pull) pour synchroniser les artefacts volumineux (données, modèles) via un stockage distant partagé.
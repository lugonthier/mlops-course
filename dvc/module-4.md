# Module 4 : Créer et Exécuter un Pipeline Simple

Mettons en pratique la création d'un pipeline DVC simple à deux étapes : préparation des données et entraînement d'un modèle.

Prérequis :
- Un projet DVC/Git initialisé.
- Un fichier de données initial (ex: `data/raw_data.csv`).
- Un fichier de paramètres params.yaml à la racine avec du contenu exemple ci-dessous:
```yaml
prepare:
  seed: 42
  split: 0.2
train:
  n_est: 100
  seed: 42 
```
- Deux scripts Python simples dans un dossier `src/` :

  - `src/prepare.py` : Lit `data/raw_data.csv`, utilise les paramètres de `params.yaml` (seed, split ratio), divise les données et écrit `data/prepared/train.csv` et `data/prepared/test.csv`.
  - `src/train.py` : Lit `data/prepared/train.csv`, utilise les paramètres de `params.yaml` (n_est, seed), entraîne un modèle simple (ex: scikit-learn) et sauvegarde le modèle dans `models/model.pkl`.
Assurez-vous que ces scripts lisent `params.yaml` (ex: avec la librairie yaml) et acceptent les chemins des fichiers en arguments.



## 1 - Définir l'Étape de Préparation (`prepare`) 

Utilisez `dvc stage add` pour définir la première étape. Cette commande crée ou met à jour `dvc.yaml`.
```bash
dvc stage add -n prepare \
              -p prepare.seed,prepare.split \
              -d src/prepare.py -d data/raw_data.csv \
              -o data/prepared \
              python src/prepare.py --raw_data_path data/raw_data.csv --output_path data/prepared
```

- `-n prepare` : Nom de l'étape.
- `-p prepare.seed,prepare.split` : Dépendance aux paramètres spécifiés dans params.yaml.
- `-d src/prepare.py -d data/raw_data.csv` : Dépendances au script et aux données brutes.
- `-o data/prepared` : Le dossier de sortie contenant train.csv et test.csv. DVC suivra ce dossier.
- `python src/prepare.py` : La commande à exécuter. (Note: le script doit savoir où lire/écrire les fichiers, soit via des arguments, soit via une configuration interne).



## 2 - Définir l'Étape d'Entraînement (`train`)
Définissez la deuxième étape qui dépend de la sortie de la première.
```bash
dvc stage add -n train \
              -p train.n_est,train.seed \
              -d src/train.py -d data/prepared \
              -o models/model.pkl \
              python src/train.py --train_data_path data/prepared/train.csv --model_output_path models/model.pkl
```

- `-n train` : Nom de l'étape.
- `-p train.n_est,train.seed` : Dépendance aux paramètres d'entraînement.
- `-d src/train.py -d data/prepared` : Dépendances au script et aux données préparées (sortie de l'étape `prepare`). DVC détecte automatiquement ce lien.
- `-o models/model.pkl` : Le fichier modèle en sortie.
- `python src/train.py` : La commande d'entraînement.




## 3 - Inspecter `dvc.yaml`
Ouvrez le fichier `dvc.yaml` qui a été créé/modifié. Il devrait contenir les définitions des deux étapes `prepare` et `train`, listant leurs `cmd`, `deps`, `params`, et `outs` respectifs.


## 4 - Commiter la Définition du Pipeline
Ajoutez `dvc.yaml` et les scripts Python (s'ils sont nouveaux ou modifiés) à Git et commitez. Ajoutez également les nouveaux .gitignore créés par DVC pour les sorties (`data/prepared/`, `models/`).
```bash
git add dvc.yaml params.yaml src/ data/.gitignore models/.gitignore
git commit -m "Define prepare and train pipeline stages"
```


## 5 - Exécuter le Pipeline
Lancez la reproduction du pipeline. Comme c'est la première fois, DVC exécutera les deux étapes dans l'ordre défini par les dépendances.
```bash
dvc repro
```
DVC affichera les étapes qu'il exécute. À la fin, les fichiers `data/prepared/train.csv`, `data/prepared/test.csv` et `models/model.pkl` auront été générés.


## 6 - Inspecter dvc.lock 
Un fichier `dvc.lock` a été créé (ou mis à jour). Ouvrez-le pour voir comment il enregistre les hashs des dépendances (params, deps) et des sorties (outs) pour chaque étape exécutée.
C'est l'empreinte de cette exécution spécifique.


## 7 - Commiter le Fichier dvc.lock
Il est essentiel de commiter `dvc.lock` pour enregistrer l'état reproductible du pipeline :
```bash
git add dvc.lock
git commit -m "Run initial pipeline"
```

## 8 - Modifier une Dépendance et Relancer

- Modifiez un paramètre dans `params.yaml`, par exemple, changez train.n_est à 150.
- Vérifiez le statut : `dvc status`. DVC devrait indiquer que l'étape train est affectée par le changement dans `params.yaml`.
- Relancez la pipeline : `dvc repro`.
- Observez que DVC devrait indiquer que l'étape prepare "didn't change, skipping" (n'a pas changé, sautée) car ses dépendances sont identiques à celles enregistrées dans `dvc.lock`. Il ne ré-exécutera que l'étape `train` (et les étapes suivantes si elles existaient).
- Le fichier `models/model.pkl` est mis à jour, et `dvc.lock` est également mis à jour pour refléter l'utilisation de n_est: 150.
- N'oubliez pas de commiter les changements :
```bash
git add params.yaml dvc.lock
git commit -m "Update n_est to 150 and rerun train stage"
```

Vous avez maintenant créé, exécuté et itéré sur un pipeline DVC simple, en voyant comment DVC gère les dépendances et assure la reproductibilité.

Note sur `dvc stage add` vs `dvc run` : Dans les anciennes versions de DVC, `dvc run` était utilisé pour créer et exécuter une étape en une seule commande. `dvc stage add` a été introduit pour séparer la définition de l'étape (mise à jour de `dvc.yaml`) de son exécution (gérée par `dvc repro`). Bien que dvc run soit obsolète, vous pourriez le rencontrer dans d'anciens tutoriels. `dvc stage add` est la commande moderne pour définir les étapes. L'option `--run` peut être ajoutée à `dvc stage add` pour exécuter immédiatement l'étape après l'avoir définie, mais l'approche recommandée est de définir les étapes puis d'utiliser `dvc repro`.
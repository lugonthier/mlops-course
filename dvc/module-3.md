# Module 3 : Partager des Données avec le Stockage Distant
Le versionnement local est utile, mais la collaboration et la sauvegarde nécessitent de pouvoir stocker et récupérer les données depuis un emplacement partagé. C'est le rôle des remotes DVC.

**Prérequis :**
- Un projet DVC/Git avec des données versionnées (Modules 1 & 2).
- Accès à un emplacement de stockage qui peut servir de remote (pour cet exemple, nous utiliserons un répertoire local externe au projet, mais les commandes sont similaires pour S3, GCS, Azure, SSH, etc.).

## 1 - Configurer un Remote DVC

**1.1 - Créer le répertoire de stockage (si local) :**

Créez un répertoire en dehors de votre projet Git/DVC qui servira de stockage.
```bash
mkdir /tmp/dvc-storage-shared
```


### 1.2 - Ajouter le remote à DVC

Utilisez `dvc remote add`. Le flag `-d` le définit comme remote par défaut, ce qui simplifie les commandes push/pull.
```bash
dvc remote add -d myremote /tmp/dvc-storage-shared
```

Ici, `myremote` est le nom que nous donnons à ce remote. DVC enregistre cette configuration dans `.dvc/config`.

### 1.3 - Commiter la configuration du remote

Pour que les collaborateurs puissent utiliser le même remote, la configuration doit être partagée via Git :
```bash
git add.dvc/config
git commit -m "Configure shared DVC remote 'myremote'"
```
Note : Si vous configurez un remote cloud (S3, GCS, Azure) nécessitant des identifiants, utilisez l'option `--local` avec `dvc remote modify` pour stocker les secrets dans `.dvc/config.local`, qui est ignoré par Git, afin de ne pas les commiter. Chaque collaborateur devra alors configurer ses propres identifiants localement.



## 2 - Pousser les Données vers le Remote
Maintenant que le remote est configuré, téléversez les données depuis votre cache local vers le stockage distant :

```bash
dvc push # Si 'myremote' n'est pas le remote par défaut: dvc push -r myremote
```


DVC va copier les fichiers correspondant aux versions de données actuellement référencées par vos fichiers `.dvc` (et potentiellement les versions précédentes présentes dans le cache) vers `/tmp/dvc-storage-shared` (ou votre remote cloud).


## 3 - Simuler un Nouveau Collaborateur/Clonage

Pour voir comment un autre utilisateur récupère les données :

### 3.1 - Cloner le dépôt Git

Simulez un nouveau collaborateur clonant le projet depuis l'hébergeur Git (ex: GitHub) :
```bash
cd ..
git clone <url_de_votre_depot_git> mon_projet_clone
cd mon_projet_clone
```

À ce stade, le collaborateur a le code et les fichiers `.dvc`, mais pas les données réelles dans `data/data.csv` (le fichier sera probablement absent ou vide). Le fichier `.dvc/config` contient la configuration du remote `myremote`.
### 3.2 - Tirer les Données depuis le Remote

Le collaborateur exécute dvc pull pour télécharger les données depuis le remote partagé vers son cache local et son espace de travail :
```bash
dvc pull # Si 'myremote' n'est pas le remote par défaut: dvc pull -r myremote
```

DVC lit les fichiers `.dvc`, trouve les hashs correspondants, télécharge les données depuis `myremote` (ici, `/tmp/dvc-storage-shared`) vers son propre cache local (`.dvc/cache`), et lie les fichiers dans l'espace de travail (recrée `data/data.csv`).



## 4 - Workflow de Mise à Jour 

Si le premier utilisateur modifie `data.csv`, fait `dvc add data/data.csv`, `git commit data/data.csv.dvc`, `git push` (pour le code et le `.dvc`), et `dvc push` (pour les données).
Le second utilisateur fait `git pull` (pour récupérer le nouveau `.dvc` et le code) puis `dvc pull` (pour télécharger la nouvelle version des données depuis le remote).


Ce processus montre comment DVC, Git et un stockage distant partagé permettent une collaboration efficace sur des projets ML impliquant des données volumineuses.
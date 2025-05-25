# Module 2 : Gérer les Versions de Données
Maintenant que nous avons une première version de nos données suivie par DVC et Git, voyons comment gérer les modifications et naviguer entre les différentes versions.

## 1 - Modifier les Données
Apportez une modification à votre fichier de données `data.csv`. Par exemple, ajoutez ou supprimez quelques lignes, modifiez des valeurs, etc.


## 2 - Vérifier le Statut DVC
Après avoir modifié un fichier suivi par DVC, la commande `dvc status` vous indiquera que le fichier a changé par rapport à la version enregistrée dans le fichier `.dvc` correspondant :
```bash
dvc status
```

Vous verrez probablement une sortie indiquant que `data.csv` a été modifié.


## 3 - Ajouter la Nouvelle Version avec DVC 

Pour enregistrer cette nouvelle version des données, utilisez à nouveau la commande `dvc add` :

```bash
dvc add data/data.csv
```
DVC va :
- Calculer le nouveau hash MD5 du fichier `data.csv` modifié.
- Mettre à jour le fichier `data/data.csv.dvc` avec ce nouveau hash et potentiellement d'autres métadonnées (comme la nouvelle taille).
- Ajouter la nouvelle version du contenu au cache DVC (sans supprimer l'ancienne, grâce au stockage adressable par contenu).


## 4 - Commiter la Nouvelle Version des Métadonnées avec Git
Le fichier `data/data.csv.dvc` a été modifié par DVC.
Pour enregistrer cette nouvelle version dans l'historique, il faut la commiter avec Git :
```bash
git add data/data.csv.dvc
git commit -m "Update data.csv with new modifications"
```
Vous avez maintenant deux commits Git, chacun pointant vers une version différente du fichier `data.csv` via le fichier `.dvc`.


## 5 - Revenir à une Version Précédente 
Supposons que vous souhaitiez revenir à la première version de `data.csv` que vous aviez commitée.

**Étape 1 : Revenir au commit Git précédent.**

Utilisez `git log` pour trouver le hash du commit où vous aviez ajouté la version initiale de `data.csv.dvc`. Ensuite, utilisez @git checkout` pour restaurer ce fichier `.dvc` spécifique :
```bash
git log --oneline data/data.csv.dvc
git checkout <hash_du_commit_precedent> -- data/data.csv.dvc
```
À ce stade, votre fichier `data/data.csv.dvc` contient les métadonnées de l'ancienne version, mais le fichier `data.csv` dans votre espace de travail est peut-être toujours la version modifiée.


**Étape 2 : Synchroniser les données avec DVC.** 

Pour mettre à jour le fichier `data.csv` dans votre espace de travail afin qu'il corresponde au fichier `.dvc` que vous venez de restaurer, utilisez `dvc checkout` :
```bash
dvc checkout data/data.csv
```
note : Vous pouvez aussi utiliser 'dvc checkout' pour synchroniser tous les fichiers suivis par DVC.

DVC va lire le hash dans `data/data.csv.dvc`, trouver le contenu correspondant dans le cache (`.dvc/cache`), et mettre à jour (ou recréer le lien vers) `data.csv` dans votre espace de travail avec cette ancienne version.


## 6 - Revenir à la Version la Plus Récente.

Pour revenir à la dernière version (celle avec les modifications), il suffit généralement de revenir au dernier commit de votre branche Git (qui contient la version la plus récente de `data/data.csv.dvc`) et de refaire un dvc checkout :
```bash
git checkout main -- data/data.csv.dvc
# Ou 'git checkout HEAD data/data.csv.dvc'
dvc checkout data/data.csv
```

Ce workflow montre comment la combinaison de `git checkout` (pour les métadonnées `.dvc`) et `dvc checkout` (pour les données réelles) permet de naviguer facilement entre les différentes versions de vos données, tout en bénéficiant de l'efficacité du cache DVC.
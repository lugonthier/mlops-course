# Module 5 : Suivre les Métriques et les Modèles
Les pipelines DVC peuvent non seulement produire des modèles, mais aussi générer et suivre des métriques de performance et des données de visualisation (plots), qui sont essentiels pour évaluer et comparer les expériences MLOps.

**Prérequis :**
- La pipeline à deux étapes (`prepare`, `train`) du module précédent.
- Modifier le script `src/train.py` pour qu'il calcule des métriques simples (ex: accuracy, loss) sur un set de validation (qu'il pourrait charger depuis `data/prepared/test.csv` ou un split interne) et les écrive dans un fichier structuré (ex: `metrics/train_metrics.json`). Il pourrait aussi générer des données pour un plot (ex: historique de la loss par epoch dans `plots/loss_history.csv`).
- Un script `src/evaluate.py` qui prend le modèle entraîné (`models/model.pkl`) et les données de test (`data/prepared/test.csv`) pour générer des métriques finales dans `metrics/eval_metrics.json`.


## 1 - Modifier/Ajouter des Étapes pour Générer Métriques et Plots

- **Option A :** Modifier l'étape train : Si `src/train.py` génère maintenant des métriques et des plots, modifiez la définition de l'étape `train` dans `dvc.yaml` (ou utilisez `dvc stage add --force -n train...` pour la redéfinir) pour inclure ces sorties :
```yaml
stages:
  train:
    cmd: python src/train.py
    deps:
      - src/train.py
      - data/prepared
    params:
      - train.n_est
      - train.seed
    outs:
      - models/model.pkl
    
    metrics:
      - metrics/train_metrics.json: # Cache: false si on ne veut pas cacher le fichier lui-même
          cache: false
    plots:
      - plots/loss_history.csv: # Cache: false ici aussi
          cache: false
          x: epoch # Optionnel: colonne pour l'axe X
          y: loss  # Optionnel: colonne pour l'axe Y
```

- `metrics:` : Définit les fichiers qui contiennent des métriques scalaires. Le format peut être JSON, YAML, TOML. `cache: false` est souvent utilisé pour les métriques/plots afin qu'ils soient directement lisibles dans le workspace et potentiellement versionnés par Git si désiré (bien que DVC puisse aussi les cacher).
- `plots:` : Définit les fichiers contenant des données pour les visualisations (JSON, YAML, CSV, TSV) ou des images (PNG, JPG, SVG). Les options `x`, `y`, `template`, `title`, etc., permettent de configurer la visualisation.


- **Option B :** Ajouter une étape `evaluate` : Si vous avez un script `src/evaluate.py`, ajoutez une nouvelle étape qui dépend du modèle et des données de test :
```bash
dvc stage add -n evaluate \
              -d src/evaluate.py -d models/model.pkl -d data/prepared/test.csv \
              -M metrics/eval_metrics.json \
              --plots-no-cache plots/eval_plots.csv \
              python src/evaluate.py --model_path models/model.pkl --test_data_path data/prepared/test.csv --metrics_output_path metrics/eval_metrics.json --plots_output_path plots/eval_plots.csv
```

- `-M metrics/eval_metrics.json` : Raccourci pour définir une sortie de métriques non cachée.
- `--plots-no-cache plots/eval_plots.csv` : Raccourci pour définir une sortie de plot non cachée.





## 2 - Reproduction du Pipeline
Exécutez `dvc repro` pour (re)générer les sorties, y compris les nouveaux fichiers de métriques et de plots.

```bash
dvc repro # Ou 'dvc repro evaluate' si vous avez ajouté une étape evaluate
```


## 3 - Visualisation des Métriques
Une fois le pipeline exécuté, utilisez `dvc metrics show` pour afficher les métriques définies dans `dvc.yaml` :
```bash
dvc metrics show
```
DVC lira les fichiers spécifiés (ex: `metrics/train_metrics.json`, `metrics/eval_metrics.json`) et affichera les valeurs dans un tableau.
Vous pouvez utiliser les options `-a` (all branches) ou `-T `(all tags) pour comparer les métriques entre différentes branches/tags Git.


## 4 - Comparaison des Métriques
Si vous avez exécuté le pipeline plusieurs fois (par exemple, après avoir changé un paramètre), vous pouvez comparer les métriques entre la version actuelle de votre espace de travail et le dernier commit Git, ou entre deux commits/branches/tags spécifiques :
```bash
# Comparer le workspace actuel avec le dernier commit (HEAD)
dvc metrics diff

# Comparer deux commits/tags/branches
dvc metrics diff <rev1> <rev2>
```

DVC affichera les métriques qui ont changé, leur ancienne et nouvelle valeur, ainsi que la différence numérique (delta).


## 5 - Visualisation des Plots

Pour visualiser les plots définis :

```bash
# Si défini dans dvc.yaml
dvc plots show

# Ou spécifier le fichier directement
dvc plots show plots/loss_history.csv
```

DVC générera un fichier HTML (par défaut dans `dvc_plots/`) que vous pouvez ouvrir dans un navigateur pour voir le graphique. Vous pouvez utiliser les options `-x`, `-y`, `-t` (template), `--title` pour personnaliser l'affichage.


## 6 - Comparaison des Plots 
De manière similaire aux métriques, vous pouvez comparer les plots entre différentes versions :
```bash# Comparer le workspace actuel avec HEAD
dvc plots diff

# Comparer plusieurs révisions (commits, tags, expériences)
dvc plots diff <rev1> <rev2> <rev3>...
```
DVC générera un fichier HTML où les différentes versions du plot sont superposées pour faciliter la comparaison visuelle.

## 7 - Commit des Résultats
N'oubliez pas de commiter les changements apportés à `dvc.yaml` (si vous l'avez modifié manuellement), le fichier `dvc.lock` mis à jour par `dvc repro`, et potentiellement les fichiers de métriques/plots si vous avez choisi de ne pas les cacher (`cache: false`) et souhaitez les versionner directement avec Git.
```bash
git add dvc.yaml dvc.lock metrics/ plots/.gitignore
git commit -m "Add metrics and plots tracking to pipeline"
```

En intégrant le suivi des métriques et des plots dans vos pipelines DVC, vous obtenez un moyen structuré et automatisé non seulement de produire des modèles, mais aussi d'évaluer quantitativement et visuellement leurs performances, ce qui est fondamental pour le cycle itératif du développement ML en MLOps.
# Travailler avec les Composants Conteneurisés
Alors que `@dsl.component` est idéal pour les fonctions Python, `@dsl.container_component` vous permet d'utiliser n'importe quelle image Docker comme étape de pipeline.

## 1 - Réécrire un composant en tant que `@dsl.container_component`.

Transformons un composant qui écrit une chaîne dans un fichier.
1. Créez un nouveau fichier Python.
2. Importez `dsl` de `kfp` et `ContainerSpec` de `kfp.dsl`.
3. Définissez une fonction Python :
   - Elle prendra une chaîne `text_to_write` en entrée et un chemin de sortie `output_file` de type `dsl.OutputPath(str)`.
   - `dsl.OutputPath(type)` est crucial : KFP injectera un chemin généré par le système où votre conteneur doit écrire son fichier de sortie.
   - Décorez cette fonction avec `@dsl.container_component`.
   - La fonction doit retourner un objet `dsl.ContainerSpec`.

L'utilisation de `dsl.OutputPath` force une gestion explicite des sorties sous forme de fichiers. KFP fournit un chemin, et le conteneur doit écrire à cet endroit. Cela rend le mécanisme de passage d'artefacts robuste et indépendant de la logique interne du conteneur.

## 2 - Utiliser le composant conteneurisé dans une pipeline

1. Dans le même fichier, définissez une pipeline `container_pipeline` qui utilise `write_to_file_container`.

## 3 -  Exécuter la pipeline du composant conteneurisé localement

note: Les composants conteneurisés nécessitent Docker pour s'exécuter localement.

1. Exécutez le script

L'utilisation de `@dsl.container_component` offre une flexibilité maximale, permettant d'exécuter n'importe quelle image Docker et d'encapsuler des dépendances complexes ou des logiques non-Python. C'est essentiel pour intégrer des outils existants ou des binaires précompilés.
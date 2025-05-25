#  Prise en Main de Kubeflow Pipelines (KFP)

L'objectif de cette première partie est de vous familiariser avec les concepts fondamentaux de Kubeflow Pipelines. Vous apprendrez à construire, compiler et exécuter des pipelines, d'abord localement, puis sur des backends KFP.

## 1 : Introduction aux Composants et Pipelines KFP

Les pipelines KFP v2 adoptent une approche plus "pythonique" grâce à l'utilisation de décorateurs, ce qui simplifie la définition des composants et des pipelines par rapport aux versions antérieures du SDK. Cela rend le code plus lisible et plus intuitif pour les développeurs Python.

| Décorateur             | Objectif                                                                      | Caractéristiques Clés                                                                                                |
| ---------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| @dsl.component         | Définit une fonction Python comme un composant KFP réutilisable.                | Encapsule une étape de la pipeline ; gère les entrées/sorties ; peut spécifier des dépendances Python (packages_to_install). |
| @dsl.container_component | Définit un composant KFP basé sur une image Docker existante.                 | Retourne un dsl.ContainerSpec ; permet d'utiliser des outils/environnements non-Python.                               |
| @dsl.pipeline          | Définit une fonction Python comme une pipeline KFP, orchestrant les composants. | Spécifie le nom, la description, les paramètres de la pipeline ; définit le graphe des tâches.                         |

## 1.1 - Créer un premier composant KFP avec @dsl.component

Un composant est l'unité de travail de base dans KFP. Il s'agit d'un programme autonome qui effectue une étape de votre workflow ML, comme le prétraitement des données, l'entraînement d'un modèle, ou l'évaluation.

1. Créez un nouveau fichier Python.
2. Importez les modules nécessaires de KFP
```python
from kfp import dsl
```
3. Définissez une fonction Python simple `say_hello` qui prend une chaîne `name` en entrée et retourne un message de salutation.
   - Pensez à utiliser les annotations de type Python pour les entrées et la sortie.
   - Décorez cette fonction avec `@dsl.component`. Le SDK KFP transformera cette fonction Python en un composant exécutable dans une pipeline.

## 1.2 Créer une première pipeline KFP avec `@dsl.pipeline`.
Une pipeline est un graphe de composants. Elle définit comment les composants sont connectés et dans quel ordre ils s'exécutent.
1. Dans le même fichier, définissez une nouvelle fonction `hello_pipeline`.
   - Cette fonction prend un paramètre `recipient` avec une valeur par défaut (par exemple, 'World'). 
   - Décorez cette fonction avec `@dsl.pipeline`, en spécifiant un `name`et une description pour votre pipeline.
   - A l'intérieur de cette fonction, instanciez votre composant `say_hello`. 

**Important** : Dans KFP, vous devez utiliser des arguments nommés lors des appel de composants dans une pipeline.

## 1.3 : Compiler la pipeline.

Avant de pouvoir exécuter une pipeline sur un backend KFP, vous devez la compiler. La compilation transforme votre code Python en une représentation statique (IR YAML) que le moteur KFP peut comprendre et exécuter. Cette IR YAML est une avancée majeure de KFP v2 car elle découple la définition de la pipeline de la plateforme d'exécution sous-jacente (comme Argo Workflows), offrant une meilleure portabilité.

1. Importez `Compiler` depuis `kfp.compiler`.
2. Ajoutez un bloc `if __name__ == '__main__':` à la fin de votre script.
3. À l'intérieur de ce bloc, utilisez `Compiler().compile()` pour compiler votre `hello_pipeline` en un fichier YAML (par exemple, `hello_pipeline.yaml`).
4. Exécutez votre script Python. Vous devriez voir un fichier `hello_pipeline.yaml` apparaître dans votre répertoire. Ouvrez-le pour inspecter sa structure.
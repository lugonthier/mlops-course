## Exécution Locale des Pipelines

KFP fournit des exécuteurs locaux qui permettent de tester rapidement vos composants et pipelines sans avoir besoin d'un cluster Kubeflow complet. C'est très utile pour le débogage initial.

Tableau : Comparaison des Exécuteurs Locaux KFP

| Exécuteur        | Isolation                         | Dépendances Requises | Types de Composants Supportés                                  | Cas d'Usage Principal                                                              |
|------------------|-----------------------------------|----------------------|----------------------------------------------------------------|------------------------------------------------------------------------------------|
| DockerRunner     | Forte (chaque tâche = conteneur)  | Docker               | Python légers, Python conteneurisés, Composants conteneurisés | Fortement recommandé ; test fidèle à l'environnement distant.                     |
| SubprocessRunner | Faible (sous-processus local)     | Python (venv optionnel) | Python légers uniquement                                       | Alternative si Docker n'est pas disponible ; moins fidèle à l'environnement distant. |

## 1 - Exécuter la pipeline localement avec `kfp.local.DockerRunner`

Le `DockerRunner` est l'option privilégiée pour l'exécution locale car il offre la meilleure isolation et simule plus fidèlement l'environnement d'exécution distant sur Kubernetes.

1. Assurez-vous que Docker est installé et en cours d'exécution sur votre machine.
2. Modifiez votre script :
   - importez `local` depuis `kfp`.
   - Dans le bloc `if __name__ == '__main__':`, commentez la partie compilation (elle n'est pas nécessaire pour l'exécution locale directe de la fonction pipeline).
   - Initialisez l'exécution local avec `local.init(runner=local.DockerRunner())`.
   - Appelez votre fonction `hello_pipeline` comme une fonction Python normale, en lui passant une valeur pour `recipient`.
   - Si votre pipeline (ou son dernier composant) retourne une valeur, vous pouvez l'assigner à une variable et l'afficher.
   - Exécutez le script. Observez les logs dans votre console. KFP va construire (ou réutiliser) une image Docker pour votre composant et l'exécuter.

## 2 - Inspecter les sorties et les logs du `DockerRunner`.


- Lorsque vous exécutez avec `local.init()`, vous pouvez spécifier un pipeline_root (par exemple, `local.init(runner=local.DockerRunner(), pipeline_root='./local_outputs')`). Les artefacts générés par les composants (si vous en aviez) seraient écrits dans ce répertoire local.   
- Les logs de KFP et de Docker fournissent des informations sur l'exécution. Pour le composant `say_hello`, le `print()` à l'intérieur de la fonction devrait apparaître dans les logs.


## 3 - Exécuter la pipeline localement avec `kfp.local.SubprocessRunner`.

Le `SubprocessRunner` est une alternative plus légère si Docker n'est pas disponible, mais il est moins robuste.   

1. Modifiez votre script pour utiliser `SubprocessRunner`.
   - Changez l'initialisation pour `local.init(runner=local.SubprocessRunner())`.`
   - Par défaut, `SubprocessRunner` essaie d'utiliser un environnement virtuel.
2. Exécutez le script.

## Les exécuteurs locaux ont des limitations importantes :   
- Pas de mise en cache des résultats des composants.
- Pas de tentatives (retries) en cas d'échec.
- Pas de gestion des ressources (CPU, mémoire, GPU).
- Certaines fonctionnalités DSL avancées (comme `dsl.Condition`, `dsl.ParallelFor`, `dsl.ExitHandler`) ne sont pas supportées.
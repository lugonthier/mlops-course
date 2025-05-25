# Interagir avec les Backends KFP

L'exécution locale est utile pour le développement, mais les pipelines sont destinées à être exécutées sur un backend KFP pour bénéficier de la scalabilité, de la persistance et des fonctionnalités complètes.


# 1 - Configurer kfp.Client pour se connecter à un backend Kubeflow Pipelines (OSS)
## 1.1 Se connecter au cluster

```bash
gcloud auth activate-service-account --key-file=<KEY_FILE_PATH>
```

```bash
gcloud container clusters get-credentials kfp --zone europe-west9-a --project formation-mlops
```
```bash
kubectl port-forward -n kubeflow svc/ml-pipeline-ui:8080:80
````

Vous pouvez ensuite explorer l'interface sur le port 8080 (localhost).

## 1.2 - Utilisation de KFP
Le client KFP (`kfp.Client`) est l'interface pour interagir avec une instance KFP déployée.

1. Assurez-vous d'avoir accès à un cluster Kubeflow avec Kubeflow Pipelines installé. Notez l'URL de l'endpoint KFP (souvent de la forme `http://<host>:<port>/pipeline`).
2. Créez un nouveau script.
3. Dans ce script, importez `kfp` et `Compiler` (si vous recompilez).
4. Définissez (ou importez) votre `hello_pipeline` et son composant `say_hello` du module 1.
5. Instanciez `kfp.Client` en lui passant l'URL de votre endpoint KFP.
   - Notes: L'authentification peut être nécessaire selon la configuration de votre cluster KFP. Pour des déploiements simples ou locaux, un accès direct peut fonctionner. Pour des déploiements plus sécurisés ou multi-utilisateurs, des mécanismes comme les cookies de session ou des jetons peuvent être requis. Consultez la documentation de votre déploiement KFP pour les détails d'authentification.
6. Exécutez le script. Si tout est configuré correctement, la pipeline sera soumise à votre cluster KFP.
7. Vérifiez l'exécution dans l'interface utilisateur de Kubeflow Pipelines. Vous devriez voir une nouvelle exécution (run) pour votre pipeline.

Le `kfp.Client`  abstrait l'interaction avec le serveur KFP. La notion de `pipeline_root` (non explicitement définie ici pour KFP OSS mais implicite dans la configuration du déploiement KFP) est fondamentale pour le stockage des artefacts sur les backends distants.


# 2 - Configurer et Exécuter une pipeline sur Vertex AI Pipelines

Vertex AI Pipelines est un service managé par Google Cloud qui peut exécuter des pipelines KFP. L'interaction se fait généralement via le SDK `google-cloud-aiplatform`.

1. Prérequis:
- Un projet Google Cloud avec l'API Vertex AI activée.
- Le SDK google-cloud-aiplatform installé (pip install `google-cloud-aiplatform`).
- Authentification configurée pour gcloud (par exemple, `gcloud auth application-default login`).
- Un bucket Google Cloud Storage (GCS) pour `pipeline_root`.

2. Modifiez votre script (ou créez-en un nouveau) pour utiliser `aiplatform.PipelineJob`.
Pour Vertex AI, l'abstraction est fournie par `google.cloud.aiplatform.PipelineJob`. Bien que KFP vise la portabilité, l'interaction avec des backends managés spécifiques peut nécessiter l'utilisation de leurs SDK natifs pour une intégration optimale, notamment pour la gestion de la configuration spécifique au cloud comme `pipeline_root` sur GCS.
# Intégration du monitoring dans un workflow (batch) ML.

## 1. Monitoring dans les pipelines ML.
Lors des pratique sur KFP nous avons développé 2 pipelines, une d'entraînement, une d'inférence. Nous allons intégrer une couche de monitoring à ces pipelines.

La couche de monitoring doit :
- Durant l'ingénierie des données : valider la stabilité et la qualité des données d'entrées.
- Durant l'entraînement : valider la qualité du modèle.
- Durant l'inférence : valider les données d'entrées ET de sorties.
- Durant le monitoring de la performance : Monitorer la qualité du modèle.

Note: KFP propose une sortie des ses composants sous forme HTML. Cette sortie sera ensuite disponible sur l'application (Kubeflow Plateform ou Vertex AI).

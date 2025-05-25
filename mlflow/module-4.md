# Déployer un Modèle MLFlow


### 1 - Déploiement du Serveur d'Inférence

Une fois votre modèle prêt, le déploiement sur un serveur local est direct. Utilisez la commande `mlflow models serve`. Cette commande démarre un serveur local qui écoute sur le port spécifié et sert votre modèle.

```bash
mlflow models serve -m runs:/<run_id>/model -p 5000
```
Dans cet exemple, remplacez `runs:/<run_id>/model` par l'URI de votre modèle. Le serveur sera alors accessible sur le port `5000`.

### 2 - Envoyer une Requête de Test

Après avoir démarré le serveur, vous pouvez lui envoyer une requête de test pour vérifier son fonctionnement. Par exemple, avec `curl` :

```bash
curl http://127.0.0.1:5000/invocations -H "Content-Type:application/json"  --data '''{"inputs": [<INPUT>]}'''
```

Cette commande envoie des données d'entrée au format JSON à votre modèle et vous devriez recevoir une prédiction en retour.

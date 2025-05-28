# Tableau de bord de surveillance de modèle ML avec une architecture en ligne

Evidently offre un service de collecte pour la surveillance en temps quasi réel. Ce service est un composant puissant qui vous permet de passer d'une surveillance par lots à une analyse continue des données de production.

## Comprendre le Service de Collecte d'Evidently

Le service de collecte fonctionne comme un agent en continu qui :

1.  **Réceptionne les Données Entrantes** : Vous envoyez des lots de nouvelles données (par exemple, les prédictions de votre modèle en production et les caractéristiques d'entrée) à un point de terminaison (endpoint) spécifique du service de collecte. Ceci est généralement fait via un client HTTP, comme le `CollectorClient` fourni par Evidently.

2.  **Calcule les Rapports ou Suites de Tests en Continu** : Une fois configuré, le collecteur exécute automatiquement les analyses que vous avez définies (Rapports ou Suites de Tests) sur les données qu'il reçoit. Il compare ces nouvelles données à un jeu de données de référence que vous lui fournissez initialement.

3.  **Fonctionne par Instantanés (Snapshots)** : Vous configurez le service pour qu'il génère ces analyses à des intervalles de temps réguliers (par exemple, toutes les 5 minutes, toutes les heures). Chaque exécution produit un "instantané" de l'état de vos données ou de la performance de votre modèle à ce moment-là. Cela élimine le besoin de scripter manuellement des tâches batch complexes.

4.  **Utilise la Même Interface Utilisateur** : Les rapports et les suites de tests générés par le service de collecte sont visualisables dans la même interface utilisateur Evidently que ceux générés par une analyse par lots. Vous bénéficiez des mêmes tableaux de bord interactifs pour explorer les résultats.

## Mise en Pratique : Exemple Détaillé

L'exemple de code ci-dessous illustre comment configurer et utiliser le service de collecte. Analysons-le étape par étape pour bien comprendre le mécanisme.

```python
import datetime
import os.path
import time
import pandas as pd

from requests.exceptions import RequestException
from sklearn import datasets

from evidently.collector.client import CollectorClient
from evidently.collector.config import CollectorConfig, IntervalTrigger, ReportConfig

from evidently.test_suite import TestSuite
from evidently.test_preset import DataDriftTestPreset

from evidently.ui.dashboards import DashboardPanelTestSuite 
from evidently.ui.dashboards import ReportFilter
from evidently.ui.dashboards import TestFilter
from evidently.ui.dashboards import TestSuitePanelType
from evidently.renderers.html_widgets import WidgetSize
from evidently.ui.workspace import Workspace

COLLECTOR_ID = "default"
COLLECTOR_TEST_ID = "default_test"

PROJECT_NAME = "Bank Marketing: online service "
WORKSACE_PATH = "bank_data"

# 1. Initialisation du Client pour communiquer avec le service de collecte
#    Assurez-vous que le service Evidently tourne sur http://localhost:8001
client = CollectorClient("http://localhost:8001")

# Chargement des données (similaire aux pratiques précédentes)
bank_marketing = datasets.fetch_openml(name="bank-marketing", as_frame="auto")
bank_marketing_data = bank_marketing.frame
reference_data = bank_marketing_data[5000:5500] # Données de référence
prod_simulation_data = bank_marketing_data[7000:] # Données pour simuler le flux de production
mini_batch_size = 50 # Taille des lots de données envoyés au collecteur

# 2. Définition de ce que le collecteur doit surveiller
def setup_test_suite():
	# On crée une Suite de Tests (ici, pour la dérive des données)
	suite = TestSuite(tests=[DataDriftTestPreset()], tags=[])
	# Exécution initiale pour valider la configuration (optionnel ici, mais bonne pratique)
	suite.run(reference_data=reference_data, current_data=prod_simulation_data[:mini_batch_size])
	# On retourne une configuration de rapport basée sur cette suite de tests
	# C'est ce que le collecteur exécutera périodiquement
	return ReportConfig.from_test_suite(suite)

# 3. Configuration de l'espace de travail et du projet Evidently (si nécessaire)
#    Ceci est pour visualiser les résultats dans l'interface utilisateur.
def workspace_setup():
	ws = Workspace.create(WORKSACE_PATH)
	project = ws.create_project(PROJECT_NAME)
	project.dashboard.add_panel(
		DashboardPanelTestSuite(
			title="Data Drift Tests (Online)",
			filter=ReportFilter(metadata_values={}, tag_values=[], include_test_suites=True),
			size=WidgetSize.HALF
		)
	)
	project.dashboard.add_panel(
		DashboardPanelTestSuite(
			title="Data Drift Tests Detailed (Online)",
			filter=ReportFilter(metadata_values={}, tag_values=[], include_test_suites=True),
			size=WidgetSize.HALF,
			panel_type=TestSuitePanelType.DETAILED
		)
	)
	project.save()

# 4. Configuration du Collecteur lui-même
def setup_config():
	ws = Workspace.create(WORKSACE_PATH)
	project = ws.search_project(PROJECT_NAME)[0]

	# Définition de la configuration du collecteur
	test_conf = CollectorConfig(
		trigger=IntervalTrigger(interval=5), # Déclencheur: toutes les 5 secondes
		report_config=setup_test_suite(),    # Ce qu'il faut exécuter (défini ci-dessus)
		project_id=str(project.id)         # Lien vers le projet Evidently pour l'UI
	)

	# Création (ou mise à jour) du collecteur sur le service Evidently
	client.create_collector(COLLECTOR_TEST_ID, test_conf)
	# Envoi des données de référence initiales au collecteur
	# Celles-ci serviront de base pour les comparaisons futures.
	client.set_reference(COLLECTOR_TEST_ID, reference_data)

# 5. Simulation de l'envoi de données en continu
def send_data():
	print("Début de l'envoi des données au collecteur...")
	for i in range(50): # Simule l'arrivée de 50 mini-lots de données
		try:
			data = prod_simulation_data[i * mini_batch_size : (i + 1) * mini_batch_size]
			# Envoi du lot de données actuel au collecteur spécifié
			client.send_data(COLLECTOR_TEST_ID, data)
			print(f"Lot {i+1} envoyé.")
		except RequestException as e:
			print(f"Erreur: Le service de collecte n'est pas disponible. {e.__class__.__name__}")
		time.sleep(1) # Pause d'1 seconde entre les envois
	print("Envoi des données terminé.")

def main():
	# S'assure que l'espace de travail et le projet existent
	if not os.path.exists(WORKSACE_PATH) or len(Workspace.create(WORKSACE_PATH).search_project(PROJECT_NAME)) == 0:
		print("Configuration de l'espace de travail Evidently...")
		workspace_setup()

	print("Configuration du collecteur...")
	setup_config()
	print("Début de la simulation d'envoi de données...")
	send_data()

if __name__ == '__main__':
	main()
```

### Explication détaillée du Code :

1.  **`client = CollectorClient("http://localhost:8001")`**
    *   Crée un objet client qui se connectera au service de collecte d'Evidently. Ce service doit être démarré séparément et écouter sur l'URL spécifiée (par défaut `http://localhost:8001` si vous lancez l'UI d'Evidently localement avec `evidently ui`).

2.  **`setup_test_suite()`**
    *   Cette fonction définit *quelle analyse* le collecteur doit effectuer. Ici, nous configurons une `TestSuite` avec `DataDriftTestPreset()`, un ensemble de tests prédéfinis pour détecter la dérive de données.
    *   `ReportConfig.from_test_suite(suite)` encapsule cette suite de tests dans une configuration que le collecteur peut utiliser.

3.  **`workspace_setup()`**
    *   Cette fonction est responsable de la mise en place du projet dans l'interface utilisateur d'Evidently. Elle crée un `Workspace` (un répertoire pour stocker les métadonnées) et un `Project` à l'intérieur.
    *   Elle ajoute des panneaux au tableau de bord de ce projet pour visualiser les résultats de la `TestSuite` que le collecteur va générer.

4.  **`setup_config()`**
    *   C'est le cœur de la configuration du collecteur.
    *   `CollectorConfig(...)`:
        *   `trigger=IntervalTrigger(interval=5)`: Indique au collecteur de s'exécuter toutes les 5 secondes. C'est ici que vous définissez la fréquence des instantanés.
        *   `report_config=setup_test_suite()`: Spécifie l'analyse à exécuter (définie dans notre fonction `setup_test_suite`).
        *   `project_id=str(project.id)`: Lie ce collecteur au projet Evidently créé précédemment, afin que les résultats apparaissent au bon endroit dans l'UI.
    *   `client.create_collector(COLLECTOR_TEST_ID, test_conf)`: Enregistre cette configuration auprès du service de collecte sous un identifiant unique (`COLLECTOR_TEST_ID`). Si un collecteur avec cet ID existe déjà, sa configuration est mise à jour.
    *   `client.set_reference(COLLECTOR_TEST_ID, reference_data)`: Envoie le jeu de données de référence au collecteur. Toutes les nouvelles données reçues par `send_data` seront comparées à ce `reference_data`.

5.  **`send_data()`**
    *   Cette fonction simule un flux de données de production arrivant au fil du temps.
    *   Elle boucle et envoie des `mini_batch_size` de `prod_simulation_data` au collecteur en utilisant `client.send_data(COLLECTOR_TEST_ID, data)`.
    *   À chaque appel de `send_data`, le collecteur reçoit ces nouvelles données. Selon sa configuration `IntervalTrigger`, il attendra le prochain intervalle de 5 secondes pour exécuter la `TestSuite` (comparant ces nouvelles données agrégées depuis le dernier run avec les données de référence) et générer un nouvel instantané.

6.  **`main()`**
    *   Orchestre l'ensemble : vérifie/configure l'espace de travail, configure le collecteur, puis démarre la simulation d'envoi de données.

## À Votre Tour : Appliquer la Surveillance en Ligne

Maintenant que vous avez une meilleure compréhension du fonctionnement du service de collecte d'Evidently et de sa configuration, il est temps de mettre ces connaissances en pratique avec vos propres données.

Reprenez les jeux de données (données de référence et données de production/actuelles) et les types d'analyses (métriques de dérive, de qualité de données, ou de performance de modèle) que vous avez explorés dans les modules précédents.

**Votre objectif est d'adapter le script ci-dessus pour mettre en place une surveillance en ligne pour votre propre cas d'usage :**

1.  **Chargement de vos données :**
    *   Modifiez le script pour charger votre propre jeu de données de référence.
    *   Préparez un jeu de données qui simulera le flux de données de production (vous pouvez découper un jeu de données existant en mini-lots).

2.  **Définition de l'analyse :**
    *   Adaptez la fonction `setup_test_suite()` (ou créez une fonction `setup_report()` si vous préférez un `Report` Evidently) pour inclure les métriques, tests ou presets pertinents pour votre cas (par exemple, `DataQualityPreset`, `RegressionPreset`, ou des tests spécifiques comme `TestColumnAllConstantValue`).

3.  **Configuration du Collecteur :**
    *   Dans `setup_config()`, ajustez le `IntervalTrigger` à une fréquence qui vous semble appropriée pour votre simulation (par exemple, 10 secondes, 1 minute).
    *   Assurez-vous que `COLLECTOR_TEST_ID` et `PROJECT_NAME` sont uniques si vous avez plusieurs configurations.

4.  **Simulation de l'envoi des données :**
    *   Modifiez la fonction `send_data()` pour qu'elle envoie vos propres mini-lots de données de production simulées.

5.  **Exécution et Visualisation :**
    *   Assurez-vous que le service UI d'Evidently est en cours d'exécution (`evidently ui` dans votre terminal, généralement depuis le répertoire `WORKSACE_PATH` ou son parent).
    *   Lancez votre script Python modifié.
    *   Observez les rapports ou suites de tests apparaître dans votre projet sur l'interface utilisateur d'Evidently à mesure que les données sont envoyées et traitées par le collecteur.

N'hésitez pas à expérimenter avec différents types de tests, de rapports, et d'intervalles de collecte pour bien maîtriser la surveillance en ligne avec Evidently.
# Projet d'Observabilité Kubernetes 📊

---

## 🚀 Introduction

Ce projet déploie une **pile d'observabilité complète** au sein d'un cluster Kubernetes, conçue pour surveiller et administrer des bases de données PostgreSQL. L'architecture est optimisée pour un environnement de développement local (via Docker Desktop) et utilise des pratiques standard de Kubernetes pour la gestion des ressources, des secrets et du routage de trafic externe.

---

## 🎯 Objectifs du Projet

Les principaux objectifs de ce projet sont les suivants :

* **Déploiement d'une Base de Données Relationnelle** : Mettre en place une instance PostgreSQL robuste et persistante.
* **Administration Simplifiée** : Fournir une interface web (pgAdmin) pour la gestion et l'exploration aisée de la base de données.
* **Visualisation et Monitoring** : Intégrer Grafana pour la création de tableaux de bord de visualisation des données et le monitoring.
* **Accès Externe Centralisé** : Utiliser un contrôleur NGINX Ingress pour gérer les requêtes entrantes et router le trafic vers les applications (pgAdmin et Grafana) via des noms d'hôtes personnalisés, sans nécessiter de spécifier les numéros de port.
* **Gestion Sécurisée des Informations Sensibles** : Stocker les identifiants de connexion (PostgreSQL, pgAdmin, Grafana) de manière sécurisée en utilisant les Secrets Kubernetes.
* **Persistance des Données** : Assurer que les données de la base de données et les configurations de Grafana persistent à travers les redémarrages de pods grâce aux Persistent Volume Claims (PVC).
* **Organisation et Isolement** : Regrouper toutes les ressources du projet dans un namespace Kubernetes dédié (`observabilite`) pour une meilleure gestion et isolation.

---

## 🛠️ Prérequis

Avant de configurer et lancer le projet, assurez-vous d'avoir les éléments suivants installés sur votre machine :

* **Docker Desktop** : Avec Kubernetes activé.
* **`kubectl`** : L'outil en ligne de commande pour interagir avec les clusters Kubernetes.
* **`helm`** : Le gestionnaire de packages pour Kubernetes (utilisé pour installer le contrôleur NGINX Ingress).
* **Python 3** : Pour exécuter le script de gestion du projet.
* **`pip`** : Le gestionnaire de packages Python.
* **`pyyaml`** : Bibliothèque Python pour lire les fichiers YAML. Installez-la avec :
    ```bash
    pip install pyyaml
    ```
* **DBeaver (Optionnel)** : Un client de base de données si vous souhaitez vous connecter directement à PostgreSQL depuis votre machine.
* **Un éditeur de texte** : Pour modifier les fichiers de configuration (ex: VS Code).

---

## ⚙️ Structure du Projet

Le projet est organisé comme suit :

projet/
├── config.yaml
├── manage_k8s_observability.py
└── kubernetes_manifests/
....├─ namespace.yaml
....├── grafana-secrets.yaml
....├── pgadmin-secrets.yaml
....├── postgres-secrets.yaml
....├── postgres-pvc.yaml
....└── postgres-service.yaml
....├── pgadmin-service.yaml
....├── grafana-service.yaml
....├── postgres-deployment.yaml
....├── pgadmin-deployment.yaml
....├── grafana-deployment.yaml
....└── ingress.yaml

---

## 🚀 Configuration et Lancement du Projet

Suivez ces étapes pour configurer et lancer l'architecture complète.

### 1. Cloner le Dépôt (si applicable) ou Créer les Fichiers

Assurez-vous que tous les fichiers YAML listés dans la section "Structure du Projet" sont bien placés dans le dossier `kubernetes_manifests` et que `config.yaml` et `manage_k8s_observability.py` sont à la racine du projet.

### 2. Personnalisation des Secrets

**⚠️ C'est une étape CRUCIALE pour la sécurité !**

Ouvrez le fichier `kubernetes_manifests/XYZ-secrets.yaml`. Vous devez **remplacer les valeurs encodées en Base64** par vos propres identifiants forts et sécurisés pour PostgreSQL, pgAdmin et Grafana.

* Pour encoder une chaîne en Base64 (sur Linux/macOS, remplacez `votre_chaine` par votre identifiant/mot de passe) :
    ```bash
    echo -n "votre_chaine" | base64
    ```
    Collez le résultat dans le fichier YAML.

Voici les clés à modifier :
* **`postgres-secrets`**:
    * `POSTGRES_USER`
    * `POSTGRES_PASSWORD`
* **`pgadmin-secrets`**:
    * `PGADMIN_DEFAULT_EMAIL`
    * `PGADMIN_DEFAULT_PASSWORD`
* **`grafana-secrets`**:
    * `GF_SECURITY_ADMIN_USER`
    * `GF_SECURITY_ADMIN_PASSWORD`

### 3. Vérification du Fichier `config.yaml`

Ouvrez le fichier `config.yaml` et assurez-vous que le `resource_directory` pointe correctement vers le dossier où se trouvent vos manifestes Kubernetes (par défaut : `kubernetes_manifests`).

```yaml
# config.yaml
namespace: observabilite
resource_directory: kubernetes_manifests # Vérifiez ce chemin
resources:
  - namespace.yaml
  - grafana-secrets.yaml
  - pgadmin-secrets.yaml
  - postgres-secrets.yaml
  - grafana-pvc.yaml
  - postgres-pvc.yaml
  - postgres-service.yaml
  - pgadmin-service.yaml
  - grafana-service.yaml
  - postgres-deployment.yaml
  - pgadmin-deployment.yaml
  - grafana-deployment.yaml
  - ingress.yaml

```

### 4. Installation du Contrôleur NGINX Ingress

Un Ingress Kubernetes nécessite un Contrôleur Ingress pour fonctionner. Nous utilisons le contrôleur NGINX Ingress, généralement installé via Helm.

1. Ajoutez le dépôt Helm :

```bash
    helm repo add ingress-nginx [https://kubernetes.github.io/ingress-nginx](https://kubernetes.github.io/ingress-nginx)
    helm repo update
```

2. Installez le contrôleur :

```bash
   helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.service.type=LoadBalancer # Nécessaire pour Docker Desktop
```

3. Récupérez l'adresse IP externe du contrôleur Ingress. C'est l'IP que vos noms d'hôtes personnalisés devront pointer :

```bash
    kubectl get services -n ingress-nginx ingress-nginx-controller
```

***Notez l'adresse IP affichée sous EXTERNAL-IP.***

5. Lancement des Ressources du Projet

Exécutez le script Python de gestion du projet :

```bash
    python3 manage_observability.py
```

Un menu interactif s'affichera :

```bash
--- 🔧 Gestion de l'Observabilité Kubernetes ---
1. ▶️ Démarrer toutes les ressources
2. 🛑 Arrêter toutes les ressources
3. 🔍 Voir le statut des Pods
4. 👻 Démarrer les ressources (Dry-Run)
5. 👻 Arrêter les ressources (Dry-Run)
6. 🚪 Quitter
------------------------------------------
```

* Choisissez l'option 1 (Démarrer toutes les ressources). Le script appliquera séquentiellement tous les manifestes YAML dans l'ordre défini par config.yaml.

6. Configuration de votre Fichier Hosts

Pour que vos noms d'hôtes personnalisés (**pgadmin.observabilite.local**, **grafana.observabilite.local**) fonctionnent, vous devez les faire pointer vers l'adresse IP externe du contrôleur NGINX Ingress (obtenue à l'étape 4.3).

* Linux/macOS : Modifiez /etc/hosts
* Windows : Modifiez C:\Windows\System32\drivers\etc\hosts (en tant qu'administrateur)

Ajoutez les lignes suivantes, en remplaçant *<EXTERNAL_IP_CONTROLLER>* par l'IP que vous avez récupérée :

```bash
    <EXTERNAL_IP_CONTROLLER> pgadmin.observabilite.local
    <EXTERNAL_IP_CONTROLLER> grafana.observabilite.local
```

---
## 🌐 Accès aux Applications

Une fois toutes les étapes terminées, vous pouvez accéder à vos applications :

* pgAdmin : Ouvrez votre navigateur et allez à http://pgadmin.observabilite.local
* Grafana : Ouvrez votre navigateur et allez à http://grafana.observabilite.local

---
## 🔑 Informations de Connexion

Voici les identifiants par défaut ou à utiliser pour les connexions :

**1. Accès pgAdmin (via navigateur) :**

* **Email** : L'email que vous avez défini dans pgadmin-secrets (ex: pgadmin4@pgadmin.org)
* **Mot de passe** : Le mot de passe que vous avez défini dans pgadmin-secrets (ex: pgadminpassword)

**2. Accès Grafana (via navigateur) :**

* **Utilisateur** : L'utilisateur que vous avez défini dans grafana-secrets (ex: admin)

* **Mot de passe** : Le mot de passe que vous avez défini dans grafana-secrets (ex: votre_mot_de_passe_grafana)

**3. Connexion à PostgreSQL (depuis DBeaver, pgAdmin, ou Grafana) :**

* **Host** : postgres-service.observabilite.svc.cluster.local
* **Port** : 5432
* **Database** : postgres
* **User** : postgres (ou celui de votre secret postgres-secrets)
* **Password** : Le mot de passe de votre secret postgres-secrets

---

## 🧹 Arrêt et Nettoyage

Pour arrêter toutes les ressources et nettoyer votre environnement Kubernetes :

1. Exécutez le script Python :

```bash
    python manage_observability.py
```

2. Choisissez l'option 2 (**Arrêter toutes les ressources**). Le script supprimera séquentiellement toutes les ressources.

3. (Optionnel) Désinstallation du contrôleur Ingress NGINX :

Si vous souhaitez désinstaller le contrôleur Ingress lui-même :

```bash
    helm uninstall ingress-nginx --namespace ingress-nginx
    kubectl delete namespace ingress-nginx
```
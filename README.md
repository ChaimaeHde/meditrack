#  MediTrack - Plateforme de Suivi des Patients Chroniques

##  Description
MediTrack est une plateforme microservices permettant le suivi à domicile des patients atteints de maladies chroniques (diabète, hypertension, insuffisance cardiaque). Elle assure la collecte des mesures, la détection automatique des anomalies, et la notification temps réel de l'équipe médicale.

## Équipe
- Chaimae HADDOUCHE - INDIA-SD
- Loubna HAOUACH - INDIA-SD

**Encadré par :** Pr. A. EL QADI

**Module :** Virtualisation et Architecture des Logiciels Distribués

##  Architecture
- **patient-profile-service** (port 8001) - Gestion des patients
- **vitals-ingestion-service** (port 8002) - Réception des mesures
- **rules-engine-service** (port 8003) - Évaluation des règles métier
- **alert-service** (port 8004) - Notifications temps réel via WebSocket
- **reporting-service** (port 8005) - Génération de rapports PDF

## Lancement

### Prérequis
- Docker Desktop installé et en cours d'exécution
- Git

### Installation
```bash
git clone https://github.com/TON-USERNAME/meditrack.git
cd meditrack
docker-compose up --build
```

### Accès aux services
- **Frontend** : http://localhost:8080
- **Documentation API** : http://localhost:8001/docs
- **Rapport patient** : http://localhost:8005/reports/weekly/1
- **MySQL** : localhost:3306 (user: meditrack, password: meditrack123)

##  Maquettes Figma
Les maquettes complètes de l'interface mobile sont disponibles ici :
[Voir les maquettes sur Figma]https://www.figma.com/design/2xnyg3qlfSg6V5UNMPdw1Q/MediTrack?node-id=2052-1969&t=3vafQCIuNv7mLpR1-1

Les exports PNG sont également disponibles dans le dossier `maquette-appli/`.

## Test rapide
1. Ouvrez http://localhost:8080
2. Sélectionnez "Ahmed Benali"
3. Choisissez "Glycémie" et entrez la valeur **3.0**
4. Cliquez "Enregistrer"
5. Deux alertes s'affichent automatiquement (critique et modérée)
6. Téléchargez le rapport PDF du patient

##  Structure du projet
\`\`\`
meditrack/
├── patient-profile-service/
├── vitals-ingestion-service/
├── rules-engine-service/
├── alert-service/
├── reporting-service/
├── frontend/
├── figma/                  (maquettes exportées)
├── docker-compose.yml
├── rules.yaml              (règles métier)
├── init.sql                (initialisation BDD)
└── README.md
\`\`\`

##  Arrêt
\`\`\`bash
docker-compose down
\`\`\`

##  Technologies utilisées
- **Backend** : Python 3.11, FastAPI, SQLAlchemy
- **Base de données** : MySQL 8.0
- **Conteneurisation** : Docker, Docker Compose
- **Frontend** : HTML5, JavaScript vanilla
- **Temps réel** : WebSocket
- **Génération PDF** : ReportLab

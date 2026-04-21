# MediTrack - Plateforme de Suivi des Patients Chroniques

## Description
Plateforme microservices pour le suivi à domicile des patients atteints de maladies chroniques (diabète, hypertension, insuffisance cardiaque).

## Architecture
- **patient-profile-service** (port 8001) : Gestion des patients
- **vitals-ingestion-service** (port 8002) : Réception des mesures
- **rules-engine-service** (port 8003) : Évaluation des règles
- **alert-service** (port 8004) : Notifications temps réel
- **reporting-service** (port 8005) : Rapports

## Lancement
```bash
docker-compose up --build
```

## Accès
- Frontend : http://localhost:8080
- MySQL : localhost:3306 (user: meditrack, password: meditrack123)
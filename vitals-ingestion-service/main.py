from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional, List
import os
import time
import requests

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://meditrack:meditrack123@mysql:3306/meditrack")
RULES_ENGINE_URL = os.getenv("RULES_ENGINE_URL", "http://rules-engine-service:8000")
ALERT_SERVICE_URL = os.getenv("ALERT_SERVICE_URL", "http://alert-service:8000")

for i in range(30):
    try:
        engine = create_engine(DATABASE_URL)
        engine.connect()
        break
    except Exception:
        time.sleep(2)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Vital(Base):
    __tablename__ = "vitals"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, index=True)
    type_mesure = Column(String(50))
    valeur = Column(Float)
    unite = Column(String(20), nullable=True)
    contexte = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class VitalCreate(BaseModel):
    patient_id: int
    type_mesure: str
    valeur: float
    unite: Optional[str] = None
    contexte: Optional[str] = None

class VitalResponse(BaseModel):
    id: int
    patient_id: int
    type_mesure: str
    valeur: float
    unite: Optional[str]
    contexte: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True

app = FastAPI(title="Vitals Ingestion Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"service": "vitals-ingestion-service", "status": "running"}

@app.post("/vitals", response_model=VitalResponse)
def create_vital(vital: VitalCreate):
    db = SessionLocal()
    try:
        db_vital = Vital(**vital.model_dump())
        db.add(db_vital)
        db.commit()
        db.refresh(db_vital)

        # Appeler le moteur de règles
        try:
            response = requests.post(
                f"{RULES_ENGINE_URL}/evaluate",
                json={
                    "patient_id": vital.patient_id,
                    "type_mesure": vital.type_mesure,
                    "valeur": vital.valeur
                },
                timeout=5
            )
            if response.status_code == 200:
                alerts = response.json().get("alerts", [])
                # Envoyer les alertes au service d'alertes
                for alert in alerts:
                    try:
                        requests.post(
                            f"{ALERT_SERVICE_URL}/alerts",
                            json={
                                "patient_id": vital.patient_id,
                                "rule_id": alert["rule_id"],
                                "severite": alert["severite"],
                                "message": alert["message"]
                            },
                            timeout=5
                        )
                    except Exception as e:
                        print(f"Erreur envoi alerte: {e}")
        except Exception as e:
            print(f"Erreur rules-engine: {e}")

        return db_vital
    finally:
        db.close()

@app.get("/vitals/{patient_id}", response_model=List[VitalResponse])
def get_patient_vitals(patient_id: int):
    db = SessionLocal()
    try:
        return db.query(Vital).filter(Vital.patient_id == patient_id).order_by(Vital.timestamp.desc()).all()
    finally:
        db.close()

@app.get("/vitals", response_model=List[VitalResponse])
def list_vitals():
    db = SessionLocal()
    try:
        return db.query(Vital).order_by(Vital.timestamp.desc()).limit(100).all()
    finally:
        db.close()
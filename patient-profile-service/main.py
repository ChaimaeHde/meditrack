from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime
from typing import Optional, List
import os
import time

# Configuration base de données
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://meditrack:meditrack123@mysql:3306/meditrack")

# Attendre que MySQL soit prêt
for i in range(30):
    try:
        engine = create_engine(DATABASE_URL)
        engine.connect()
        print("Connexion MySQL OK")
        break
    except Exception as e:
        print(f"Attente MySQL... ({i+1}/30)")
        time.sleep(2)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèle SQLAlchemy
class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100))
    prenom = Column(String(100))
    date_naissance = Column(Date)
    pathologies = Column(String(255))
    medecin_id = Column(Integer, nullable=True)
    telephone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    date_creation = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Schémas Pydantic
class PatientCreate(BaseModel):
    nom: str
    prenom: str
    date_naissance: Optional[date] = None
    pathologies: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None

class PatientResponse(BaseModel):
    id: int
    nom: str
    prenom: str
    date_naissance: Optional[date]
    pathologies: Optional[str]
    telephone: Optional[str]
    email: Optional[str]

    class Config:
        from_attributes = True

# Application FastAPI
app = FastAPI(title="Patient Profile Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"service": "patient-profile-service", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/patients", response_model=PatientResponse)
def create_patient(patient: PatientCreate):
    db = SessionLocal()
    try:
        db_patient = Patient(**patient.model_dump())
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        return db_patient
    finally:
        db.close()

@app.get("/patients", response_model=List[PatientResponse])
def list_patients():
    db = SessionLocal()
    try:
        return db.query(Patient).all()
    finally:
        db.close()

@app.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int):
    db = SessionLocal()
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient non trouvé")
        return patient
    finally:
        db.close()

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int):
    db = SessionLocal()
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient non trouvé")
        db.delete(patient)
        db.commit()
        return {"message": "Patient supprimé"}
    finally:
        db.close()
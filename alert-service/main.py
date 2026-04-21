from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional, List
import os
import time
import json
import asyncio

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://meditrack:meditrack123@mysql:3306/meditrack")

for i in range(30):
    try:
        engine = create_engine(DATABASE_URL)
        engine.connect()
        break
    except Exception:
        time.sleep(2)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, index=True)
    rule_id = Column(String(100))
    severite = Column(String(20))
    message = Column(Text)
    statut = Column(String(20), default="nouvelle")
    timestamp = Column(DateTime, default=datetime.utcnow)
    acquittee_par = Column(String(100), nullable=True)

Base.metadata.create_all(bind=engine)

class AlertCreate(BaseModel):
    patient_id: int
    rule_id: str
    severite: str
    message: str

class AlertResponse(BaseModel):
    id: int
    patient_id: int
    rule_id: str
    severite: str
    message: str
    statut: str
    timestamp: datetime
    acquittee_par: Optional[str]

    class Config:
        from_attributes = True

app = FastAPI(title="Alert Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gestion des connexions WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.get("/")
def root():
    return {"service": "alert-service", "status": "running"}

@app.post("/alerts", response_model=AlertResponse)
async def create_alert(alert: AlertCreate):
    db = SessionLocal()
    try:
        db_alert = Alert(**alert.model_dump())
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)

        # Notifier via WebSocket
        await manager.broadcast({
            "type": "new_alert",
            "id": db_alert.id,
            "patient_id": db_alert.patient_id,
            "severite": db_alert.severite,
            "message": db_alert.message,
            "timestamp": db_alert.timestamp.isoformat()
        })

        # Simulation d'envoi SMS/Email (log uniquement)
        print(f"[ALERT] Patient {alert.patient_id} - {alert.severite}: {alert.message}")

        return db_alert
    finally:
        db.close()

@app.get("/alerts", response_model=List[AlertResponse])
def list_alerts():
    db = SessionLocal()
    try:
        return db.query(Alert).order_by(Alert.timestamp.desc()).limit(50).all()
    finally:
        db.close()

@app.get("/alerts/patient/{patient_id}", response_model=List[AlertResponse])
def get_patient_alerts(patient_id: int):
    db = SessionLocal()
    try:
        return db.query(Alert).filter(Alert.patient_id == patient_id).order_by(Alert.timestamp.desc()).all()
    finally:
        db.close()

@app.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, user: str = "medecin"):
    db = SessionLocal()
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alerte non trouvée")
        alert.statut = "acquittee"
        alert.acquittee_par = user
        db.commit()
        return {"message": "Alerte acquittée"}
    finally:
        db.close()

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
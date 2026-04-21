from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import os
import time

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://meditrack:meditrack123@mysql:3306/meditrack")

for i in range(30):
    try:
        engine = create_engine(DATABASE_URL)
        engine.connect()
        break
    except Exception:
        time.sleep(2)

app = FastAPI(title="Reporting Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"service": "reporting-service", "status": "running"}

@app.get("/reports/weekly/{patient_id}")
def weekly_report(patient_id: int):
    with engine.connect() as conn:
        patient = conn.execute(
            text("SELECT * FROM patients WHERE id = :id"),
            {"id": patient_id}
        ).fetchone()

        if not patient:
            return {"error": "Patient non trouvé"}

        date_limite = datetime.utcnow() - timedelta(days=7)
        vitals = conn.execute(
            text("SELECT * FROM vitals WHERE patient_id = :id AND timestamp >= :date ORDER BY timestamp DESC"),
            {"id": patient_id, "date": date_limite}
        ).fetchall()

        alerts = conn.execute(
            text("SELECT * FROM alerts WHERE patient_id = :id AND timestamp >= :date ORDER BY timestamp DESC"),
            {"id": patient_id, "date": date_limite}
        ).fetchall()

    # Génération PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, height - 50, "Rapport Hebdomadaire - MediTrack")

    p.setFont("Helvetica", 12)
    p.drawString(50, height - 90, f"Patient: {patient.prenom} {patient.nom}")
    p.drawString(50, height - 110, f"Pathologies: {patient.pathologies or 'Non renseigné'}")
    p.drawString(50, height - 130, f"Période: {date_limite.strftime('%d/%m/%Y')} - {datetime.utcnow().strftime('%d/%m/%Y')}")

    y = height - 180
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, f"Mesures enregistrées ({len(vitals)})")
    y -= 30

    p.setFont("Helvetica", 10)
    for vital in vitals[:20]:
        ts = vital.timestamp.strftime('%d/%m %H:%M') if vital.timestamp else ''
        p.drawString(50, y, f"{ts} - {vital.type_mesure}: {vital.valeur} {vital.unite or ''}")
        y -= 15
        if y < 100:
            p.showPage()
            y = height - 50

    y -= 20
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, f"Alertes ({len(alerts)})")
    y -= 30

    p.setFont("Helvetica", 10)
    for alert in alerts[:10]:
        ts = alert.timestamp.strftime('%d/%m %H:%M') if alert.timestamp else ''
        p.drawString(50, y, f"{ts} [{alert.severite}] {alert.message[:80]}")
        y -= 15
        if y < 100:
            p.showPage()
            y = height - 50

    p.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=rapport_{patient_id}.pdf"}
    )

@app.get("/reports/summary/{patient_id}")
def summary(patient_id: int):
    with engine.connect() as conn:
        nb_vitals = conn.execute(
            text("SELECT COUNT(*) FROM vitals WHERE patient_id = :id"),
            {"id": patient_id}
        ).scalar()
        nb_alerts = conn.execute(
            text("SELECT COUNT(*) FROM alerts WHERE patient_id = :id"),
            {"id": patient_id}
        ).scalar()

    return {
        "patient_id": patient_id,
        "total_mesures": nb_vitals,
        "total_alertes": nb_alerts
    }
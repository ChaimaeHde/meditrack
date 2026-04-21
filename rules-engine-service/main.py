from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yaml
import os

app = FastAPI(title="Rules Engine Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger les règles au démarrage
RULES_FILE = os.getenv("RULES_FILE", "/app/rules.yaml")
rules_data = {"rules": []}

try:
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        rules_data = yaml.safe_load(f)
        print(f"Règles chargées: {len(rules_data.get('rules', []))}")
except Exception as e:
    print(f"Erreur chargement règles: {e}")

class EvaluateRequest(BaseModel):
    patient_id: int
    type_mesure: str
    valeur: float

@app.get("/")
def root():
    return {"service": "rules-engine-service", "status": "running"}

@app.get("/rules")
def get_rules():
    return rules_data

@app.post("/evaluate")
def evaluate(request: EvaluateRequest):
    triggered_alerts = []

    for rule in rules_data.get("rules", []):
        if rule.get("parametre") != request.type_mesure:
            continue

        operateur = rule.get("operateur")
        seuil = rule.get("seuil")
        declenche = False

        if operateur == ">" and request.valeur > seuil:
            declenche = True
        elif operateur == "<" and request.valeur < seuil:
            declenche = True
        elif operateur == ">=" and request.valeur >= seuil:
            declenche = True
        elif operateur == "<=" and request.valeur <= seuil:
            declenche = True
        elif operateur == "==" and request.valeur == seuil:
            declenche = True

        if declenche:
            triggered_alerts.append({
                "rule_id": rule.get("id"),
                "severite": rule.get("severite"),
                "message": rule.get("message"),
                "pathologie": rule.get("pathologie")
            })

    return {
        "patient_id": request.patient_id,
        "type_mesure": request.type_mesure,
        "valeur": request.valeur,
        "alerts": triggered_alerts
    }
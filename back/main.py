from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="STARS API", description="Satellite Tracking and Anomaly Response System", version="1.0.0")
DATA_FILE = "satellites.json"
GROUPS_FILE = "groups.json"

class Satellite(BaseModel):
    name: str
    norad: str
    orbit: str
    mission: str
    alt: float
    inc: float
    ecc: float
    mm: float
    mmc: str
    tle1: Optional[str] = ""
    tle2: Optional[str] = ""

class AnalyzeRequest(BaseModel):
    name: str
    orbit: str
    alt: float
    inc: float
    ecc: float
    mm: float
    mmc: str
    mission: str

class Group(BaseModel):
    group_name: str
    satellite_names: List[str]

def load_satellites():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_satellites(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_groups():
    if not os.path.exists(GROUPS_FILE):
        return {}
    with open(GROUPS_FILE, "r") as f:
        return json.load(f)

def save_groups(data):
    with open(GROUPS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def calculate_risk(alt, ecc, mmc, orbit, mission, inc):
    score = 0
    reasons = []

    if ecc > 0.3:
        score += 35
        reasons.append("Very high eccentricity — possible uncontrolled orbit or HEO profile.")
    elif ecc > 0.1:
        score += 15
        reasons.append("Elevated eccentricity detected — monitor for orbital instability.")

    if mmc == "High":
        score += 40
        reasons.append("Significant mean motion change — possible maneuver or atmospheric drag event.")
    elif mmc == "Medium":
        score += 20
        reasons.append("Moderate mean motion variation — compare with next TLE epoch.")

    if orbit == "LEO" and alt < 400:
        score += 20
        reasons.append("Critically low LEO altitude — reentry risk within months due to atmospheric drag.")

    if mission == "Unknown Object":
        score += 20
        reasons.append("Unidentified object — no operator data available, high uncertainty.")

    if inc > 85 and inc < 95:
        score += 5
        reasons.append("Near-polar orbit — increased conjunction risk with other polar satellites.")

    score = min(score, 100)

    if score >= 70:
        risk_level = "High"
        strategy = [
            "Immediate optical/RF cross-validation recommended.",
            "Priority tracking flag — escalate to SDA operator.",
            "Conjunction screening required — compute TCA with nearby objects.",
            "Propagate with latest TLE and compare against predicted ephemeris.",
            "Reentry risk monitoring recommended." if alt < 400 else "Check for active maneuver — compare BSTAR drag term.",
            "High eccentricity — possible uncontrolled tumbling, request optical observation." if ecc > 0.3 else "Monitor next 3 TLE updates for persistent anomaly.",
        ]
        validation_plan = [
            "Cross-check with Space-Track.org catalog for latest TLE epoch",
            "Run SGP4 propagation and compare predicted vs observed state vector",
            "Request optical observation during next pass window",
            "Perform RF signal monitoring to detect active maneuver",
            "Check conjunction data messages (CDMs) for close approach events",
            "Notify SDA operator if anomaly persists beyond 2 TLE updates"
        ]
    elif score >= 35:
        risk_level = "Medium"
        strategy = [
            "SGP4 propagation comparison recommended — compare predicted vs updated TLE.",
            "Monitor mean motion trend over next 3 TLE epochs.",
            "Check for maneuver announcements from satellite operator.",
            "Verify BSTAR drag coefficient for atmospheric drag assessment.",
            "Flag for escalation if anomaly trend persists beyond 24 hours.",
        ]
        validation_plan = [
            "Download latest TLE from Space-Track.org and compare mean motion delta",
            "Propagate with SGP4 and compare predicted vs updated orbit",
            "Monitor BSTAR drag term for atmospheric drag assessment",
            "Flag for escalation if anomaly trend continues over next 24 hours"
        ]
    else:
        risk_level = "Low"
        strategy = [
            "Routine TLE monitoring — verify next update within standard cycle.",
            "Maintain standard tracking cadence — no immediate action required.",
            "Confirm ground track repeatability for Earth observation missions." if mission == "Earth Observation" else "No cross-validation required at this time.",
        ]
        validation_plan = [
            "Verify next TLE update within standard 24-48 hour cycle",
            "Confirm ground track repeatability for mission continuity",
            "No cross-validation required at this time"
        ]

    anomaly_status = "Anomaly candidate detected" if score >= 35 else "No anomaly detected"
    reason_text = " ".join(reasons) if reasons else "Parameters within nominal range for mission profile."

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "anomaly_status": anomaly_status,
        "anomaly_reason": reason_text,
        "recommended_strategy": strategy,
        "follow_up_action": "Use optical observation or RF monitoring for cross-validation." if score >= 35 else "Continue routine monitoring.",
        "validation_plan": validation_plan
    }

@app.get("/")
def root():
    return {"service": "STARS API", "description": "Satellite Tracking and Anomaly Response System", "version": "1.0.0"}

@app.get("/satellites")
def get_satellites():
    logger.info("GET /satellites")
    return load_satellites()

@app.post("/satellites")
def register_satellite(sat: Satellite):
    logger.info(f"POST /satellites | name={sat.name}")
    data = load_satellites()
    sat_dict = sat.dict()
    data.append(sat_dict)
    save_satellites(data)
    return {"msg": "Satellite registered successfully", "satellite": sat_dict}

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    logger.info(f"POST /analyze | name={req.name} | orbit={req.orbit} | alt={req.alt}")
    result = calculate_risk(req.alt, req.ecc, req.mmc, req.orbit, req.mission, req.inc)
    logger.info(f"Result | risk_level={result['risk_level']} | score={result['risk_score']}")
    return result

@app.get("/satellites/{name}")
def get_satellite(name: str):
    logger.info(f"GET /satellites/{name}")
    data = load_satellites()
    for s in data:
        if s["name"].lower() == name.lower():
            return s
    raise HTTPException(status_code=404, detail="Satellite not found")

@app.get("/groups")
def get_groups():
    logger.info("GET /groups")
    return load_groups()

@app.post("/groups")
def create_group(group: Group):
    logger.info(f"POST /groups | name={group.group_name}")
    groups = load_groups()
    groups[group.group_name] = group.satellite_names
    save_groups(groups)
    return {"msg": f"Group {group.group_name} created.", "group": groups[group.group_name]}

@app.delete("/groups/{group_name}")
def delete_group(group_name: str):
    logger.info(f"DELETE /groups/{group_name}")
    groups = load_groups()
    if group_name not in groups:
        raise HTTPException(status_code=404, detail="Group not found")
    del groups[group_name]
    save_groups(groups)
    return {"msg": f"Group {group_name} deleted."}
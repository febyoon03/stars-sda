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
        reasons.append("매우 높은 이심률 — 비제어 궤도 또는 HEO 프로파일 가능성.")
    elif ecc > 0.1:
        score += 15
        reasons.append("이심률 상승 감지 — 궤도 불안정성 모니터링 필요.")

    if mmc == "High":
        score += 40
        reasons.append("평균 운동 변화량 높음 — 기동 또는 대기권 항력 이벤트 가능성.")
    elif mmc == "Medium":
        score += 20
        reasons.append("중간 수준의 평균 운동 변화 — 다음 TLE 에포크와 비교 필요.")

    if orbit == "LEO" and alt < 400:
        score += 20
        reasons.append("LEO 임계 저고도 — 대기권 항력으로 인한 수개월 내 재진입 위험.")

    if mission == "Unknown Object":
        score += 20
        reasons.append("미확인 물체 — 운용 데이터 없음, 불확실성 높음.")

    if inc > 85 and inc < 95:
        score += 5
        reasons.append("근극궤도 — 다른 극궤도 위성과의 충돌 위험 증가.")

    score = min(score, 100)

    if score >= 70:
        risk_level = "High"
        strategy = [
            "즉각적인 광학/RF 교차 검증 권장.",
            "우선 추적 플래그 설정 — SDA 운용자에게 에스컬레이션.",
            "충돌 스크리닝 필요 — 인접 물체와의 TCA 계산.",
            "최신 TLE로 전파 후 예측 위성력과 비교.",
            "재진입 위험 모니터링 권장." if alt < 400 else "활성 기동 확인 — BSTAR 항력 계수 비교.",
            "높은 이심률 — 비제어 텀블링 가능성, 광학 관측 요청." if ecc > 0.3 else "다음 3회 TLE 업데이트 모니터링.",
        ]
        validation_plan = [
            "Space-Track.org 카탈로그에서 최신 TLE 에포크 교차 확인",
            "SGP4 전파 실행 후 예측 대 관측 상태벡터 비교",
            "다음 패스 윈도우에서 광학 관측 요청",
            "RF 신호 모니터링으로 활성 기동 탐지",
            "근접 접근 이벤트에 대한 CDM(Conjunction Data Message) 확인",
            "2회 TLE 업데이트 이후에도 이상 지속 시 SDA 운용자 통보"
        ]
    elif score >= 35:
        risk_level = "Medium"
        strategy = [
            "SGP4 전파 비교 권장 — 예측 대 업데이트 TLE 비교.",
            "다음 3회 TLE 에포크에 걸쳐 평균 운동 추세 모니터링.",
            "위성 운용자의 기동 공지 확인.",
            "대기권 항력 평가를 위한 BSTAR 항력 계수 검증.",
            "24시간 이내 이상 추세 지속 시 에스컬레이션 플래그 설정.",
        ]
        validation_plan = [
            "Space-Track.org에서 최신 TLE 다운로드 후 평균 운동 델타 비교",
            "SGP4 전파 후 예측 대 업데이트 궤도 비교",
            "대기권 항력 평가를 위한 BSTAR 항력 계수 모니터링",
            "다음 24시간 이내 이상 추세 지속 시 에스컬레이션 플래그 설정"
        ]
    else:
        risk_level = "Low"
        strategy = [
            "정기 TLE 모니터링 — 표준 주기 내 다음 업데이트 확인.",
            "표준 추적 주기 유지 — 즉각적인 조치 불필요.",
            "지구 관측 임무 연속성을 위한 지상 트랙 반복성 확인." if mission == "Earth Observation" else "현재 교차 검증 불필요.",
        ]
        validation_plan = [
            "표준 24~48시간 주기 내 다음 TLE 업데이트 확인",
            "임무 연속성을 위한 지상 트랙 반복성 확인",
            "현재 교차 검증 불필요"
        ]

    anomaly_status = "이상 후보 감지됨" if score >= 35 else "이상 없음"
    reason_text = " ".join(reasons) if reasons else "임무 프로파일 기준 정상 범위 내 파라미터."

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "anomaly_status": anomaly_status,
        "anomaly_reason": reason_text,
        "recommended_strategy": strategy,
        "follow_up_action": "교차 검증을 위해 광학 관측 또는 RF 모니터링 활용 권장." if score >= 35 else "정기 모니터링 계속.",
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
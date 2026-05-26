# STARS — 위성 추적 및 이상 대응 추천 시스템

**SDA 프로토타입 v1.0** · Streamlit + FastAPI + Docker + AWS EC2

---

## 프로젝트 개요

STARS(Satellite Tracking and Anomaly Response System)는 TLE 기반 위성 궤도 파라미터를 분석하여 이상 후보를 탐지하고, SDA(우주 상황 인식) 관점의 대응 전략을 추천하는 웹 기반 프로토타입 시스템입니다.

본 프로젝트는 다음 기술들을 하나의 시스템으로 통합하여 구현되었습니다.

- Streamlit 프론트엔드
- FastAPI 백엔드
- Docker 컨테이너화
- AWS EC2 배포

---

## 시스템 구조
사용자 입력
↓
Streamlit 프론트엔드 (포트 80)
↓ HTTP 요청
FastAPI 백엔드 (포트 8000)
↓
위험도 분석 및 대응 전략 추천 엔진
↓
JSON 응답
↓
Streamlit 시각화 대시보드

---

## 주요 기능

### 1. 위성 궤도 시각화
- 지구 중심 궤도 시각화
- 궤도 유형별 위성 구분 (LEO / MEO / GEO / HEO)
- 위성 선택 및 탐색

### 2. 위성 검색 및 필터링
- 위성 이름 검색
- 궤도 유형 필터링
- 사용자 정의 그룹 생성

### 3. TLE 기반 위험 분석
다음 궤도 파라미터를 활용한 rule-based 위험 분석:
- 고도 (Altitude)
- 이심률 (Eccentricity)
- 경사각 (Inclination)
- 평균 운동 변화량 (Mean Motion Change)
- 궤도 유형 (Orbit Regime)
- 임무 유형 (Mission Type)

분석 결과:
- 이상 후보 점수 (0~100)
- 위험 등급 (낮음 / 보통 / 높음)
- 의심 원인
- SDA 대응 전략
- 검증 계획

### 4. 위성 등록
- 위성 이름, NORAD ID, 궤도 유형, 임무 유형, TLE 정보 입력
- 등록된 위성 대시보드 모니터링

### 5. 그룹 모니터링
- 위성 그룹 생성 및 관리
- 그룹별 필터링 모니터링

---

## 기술 스택

| 구성 요소 | 기술 |
|-----------|------|
| 프론트엔드 | Streamlit |
| 백엔드 | FastAPI |
| 컨테이너화 | Docker |
| 배포 환경 | AWS EC2 (Amazon Linux 2023) |
| 언어 | Python 3.11 |
| 시각화 | Plotly |

---

## 프로젝트 구조
stars-sda/
├── front/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── back/
│   ├── main.py
│   ├── satellites.json
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md

---

## 샘플 위성 20개

| 위성 | 궤도 | 임무 |
|------|------|------|
| ISS | LEO | 과학 |
| NOAA-20 | LEO | 지구 관측 |
| LANDSAT-8 | LEO | 지구 관측 |
| SENTINEL-2A | LEO | 지구 관측 |
| TERRA | LEO | 지구 관측 |
| STARLINK-1 | LEO | 통신 |
| IRIDIUM-100 | LEO | 통신 |
| SWARM-A | LEO | 과학 |
| CRYOSAT-2 | LEO | 과학 |
| GPS IIF-1 | MEO | 항법 |
| GALILEO-1 | MEO | 항법 |
| GLONASS-M | MEO | 항법 |
| INTELSAT-19 | GEO | 통신 |
| GOES-16 | GEO | 지구 관측 |
| ASTRA-1N | GEO | 통신 |
| BEIDOU-G1 | GEO | 항법 |
| SBIRS-GEO-1 | GEO | 과학 |
| MOLNIYA-3 | HEO | 통신 |
| TUNDRA-1 | HEO | 통신 |
| UNKNOWN-OBJ | LEO | 미확인 물체 |

---

## 배포 주소

- GitHub: https://github.com/febyoon03/stars-sda
- 배포 주소: http://54.209.5.45 (AWS EC2 · Learner Lab)

---

## 개발자

**이윤경 (Yoonkyong Lee)**
광운대학교 정보융합학과

관심 분야:
- 우주 상황 인식 (SDA)
- 미션 데이터 시스템
- 궤도 데이터 분석
- 항공우주 데이터 엔지니어링

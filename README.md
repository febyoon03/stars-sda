# STARS — Satellite Tracking and Anomaly Response System

**SDA Prototype v1.0** · Streamlit + FastAPI + Docker + AWS EC2

---

## Overview

STARS (Satellite Tracking and Anomaly Response System) is a web-based prototype dashboard that analyzes orbital anomaly candidates based on TLE-derived parameters and recommends SDA (Space Domain Awareness) response strategies.

This project integrates the following technologies into a single end-to-end system:

- Streamlit Frontend
- FastAPI Backend
- Docker Containerization
- AWS EC2 Deployment

STARS visualizes representative satellites by orbit type (LEO, MEO, GEO, HEO), performs simplified rule-based risk analysis using orbital mechanics parameters, and recommends SDA response strategies as a decision-support dashboard.

This system is designed as a lightweight prototype to connect SDA concepts with web-based data systems at the undergraduate level — not as an operational space surveillance system.

---

## Motivation

The orbital environment is becoming increasingly complex due to the growing number of operational satellites, expanding satellite constellations, and rising space debris.

Modern SDA systems must continuously monitor:

- Orbital decay
- Maneuver suspicion
- Conjunction risk
- Abnormal orbital changes
- Observation gaps

This project goes beyond a simple recommendation app by connecting real aerospace and SDA concepts — including orbital data interpretation, anomaly candidate flagging, response strategy recommendation, visualization, and cloud-based deployment — into a single system.

---

## Key Features

### 1. Orbital Visualization Dashboard
- Earth-centered orbit visualization
- Satellite classification by orbit type (LEO / MEO / GEO / HEO)
- Satellite selection and exploration

### 2. Satellite Search and Filtering
- Satellite name search
- Orbit group filtering
- Custom group creation for targeted monitoring

### 3. TLE-Based Risk Analysis
Rule-based risk analysis using the following orbital parameters:
- Altitude
- Eccentricity
- Inclination
- Mean Motion Change
- Orbit Regime
- Mission Type

Results include:
- Anomaly Candidate Score (0–100)
- Risk Level (Low / Medium / High)
- Suspected Orbital Concern
- SDA Response Recommendation
- Validation Plan

### 4. SDA Response Recommendation
Response strategies recommended based on orbital characteristics:
- Routine Monitoring
- SGP4 Propagation Comparison
- Optical / RF Cross-Validation
- Orbital Decay Monitoring
- Conjunction Screening Preparation

### 5. Satellite Registration
Users can register satellites of interest by providing:
- Satellite Name
- NORAD ID
- Orbit Type
- Mission Type
- TLE Line 1 / Line 2
- Orbital Parameters

### 6. Custom Group Monitoring
Users can create satellite groups for focused monitoring and filtering.

---

## System Architecture
User
↓
Streamlit Frontend (Port 80)
↓ HTTP Request
FastAPI Backend (Port 8000)
↓
Risk Analysis & Recommendation Engine
↓
JSON Response
↓
Streamlit Visualization Dashboard

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI |
| Containerization | Docker |
| Deployment | AWS EC2 (Amazon Linux 2023) |
| Language | Python 3.11 |
| Visualization | Plotly |

---

## Project Structure
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

## Sample Satellites (20 satellites)

| Satellite | Orbit | Mission |
|-----------|-------|---------|
| ISS | LEO | Scientific |
| NOAA-20 | LEO | Earth Observation |
| LANDSAT-8 | LEO | Earth Observation |
| SENTINEL-2A | LEO | Earth Observation |
| TERRA | LEO | Earth Observation |
| STARLINK-1 | LEO | Communication |
| IRIDIUM-100 | LEO | Communication |
| SWARM-A | LEO | Scientific |
| CRYOSAT-2 | LEO | Scientific |
| GPS IIF-1 | MEO | Navigation |
| GALILEO-1 | MEO | Navigation |
| GLONASS-M | MEO | Navigation |
| INTELSAT-19 | GEO | Communication |
| GOES-16 | GEO | Earth Observation |
| ASTRA-1N | GEO | Communication |
| BEIDOU-G1 | GEO | Navigation |
| SBIRS-GEO-1 | GEO | Scientific |
| MOLNIYA-3 | HEO | Communication |
| TUNDRA-1 | HEO | Communication |
| UNKNOWN-OBJ | LEO | Unknown Object |

---

## Project Scope

This project is a prototype implementation at the undergraduate level, not an operational SDA system.

The current system operates based on:
- Representative sample satellites
- User-registered satellites
- Simplified rule-based analysis

The following features are intentionally out of scope:
- Real-time global satellite catalog
- Precise Orbit Determination
- Operational collision probability calculation
- Certified conjunction analysis

These limitations reflect a design choice to focus on SDA workflow, orbital data interpretation, web-based monitoring architecture, and frontend/backend integration within the scope of an undergraduate project.

---

## Limitations

This system does not provide:
- Authoritative orbital determination
- Precise maneuver detection
- Operational collision assessment
- Certified conjunction analysis

Analysis results should be interpreted as anomaly candidate flagging and decision-support recommendations — not as definitive operational judgments.

---

## Future Work

1. **Real-Time TLE Integration** — CelesTrak / Space-Track API connection
2. **Expanded SDA Analytics** — SGP4 propagation comparison, TLE trend analysis
3. **Multi-Satellite Monitoring** — Mission-priority grouping, operator-specific lists
4. **Advanced Visualization** — Real-time orbit propagation, interactive 3D rendering
5. **AI-Based Orbital Analysis** — Anomaly detection model, maneuver classification

---

## Live Demo

- GitHub: https://github.com/febyoon03/stars-sda
- Deployed: http://54.209.5.45 (AWS EC2 · Learner Lab)

---

## Author

**Yoonkyong Lee (이윤경)**
Department of Information Convergence, Kwangwoon University

Areas of Interest:
- Space Domain Awareness (SDA)
- Mission Data Systems
- Orbital Data Analysis
- Aerospace Data Engineering
- EO / RF Data Fusion

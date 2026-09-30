# Adaptive Exam Operations & Schedule Recovery System
> *"A timetable that can survive reality."*

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![AI-Powered](https://img.shields.io/badge/AI-Gemini%201.5%20Flash%20%7C%20Heuristic%20Dual--Mode-8E75C2)](https://ai.google.dev/)
[![Hackathon](https://img.shields.io/badge/HACKSPRINT'26-Agentic%20AI%20Track-FF6B6B)](#)

An autonomous **Agentic AI system** designed to solve the critical flaw of traditional university exam scheduling: **real-world operational disruptions**. Rather than generating a rigid, static timetable that breaks on exam day, this system autonomously senses disruptions (hall flooding, professor medical emergencies, compound resource failures), detects constraint violations across 8 hard institutional rules (H1–H8), computes minimal-ripple repairs, and dispatches instant updates to affected faculty.

---

## 🌟 Key Features

1. **Autonomous Agentic Recovery Loop**:
   - `PLAN` → `VALIDATE` → `DISRUPT` → `DETECT` → `REPAIR` → `VERIFY` → `EXPLAIN`
   - Zero manual intervention required to resolve multi-resource scheduling crises.
2. **Dual-Mode AI Engine**:
   - **Live Mode**: Google Gemini 1.5 Flash via REST API for natural language copilot parsing and deep decision rationale.
   - **Local Heuristic Mode**: Instant 0.003-second deterministic fail-safe fallback ensuring 100% offline operational resilience.
3. **8-Point Hard Constraint Compliance (H1–H8)**:
   - **H1**: Student Exam Overlap Prevention
   - **H2**: Examination Hall Capacity Enforcement
   - **H3**: Hall Operational Availability
   - **H3b**: Room Collision & Double-Booking Avoidance
   - **H4**: Faculty Timetable Freedom (No lecture/teaching clash)
   - **H5**: Explicit Faculty Duty Confirmation
   - **H6**: Physical Campus Presence / Check-In Verification
   - **H7**: Faculty Double-Booking Prevention
   - **H8**: Mobility Accessibility Compliance (Mandatory ground-floor venues for students with special needs)
4. **Natural Language Coordinator Copilot**:
   - Emergency dispatchers can input plain English reports: *"Room R102 flooded, switch to backup"* or *"Dr. Priya Sharma is unavailable in slot T1"*.
5. **Multi-Department Faculty Registry & Candidate Pool**:
   - 12 real professors across CSE, ECE, IT, and Mechanical departments.
   - Daily teaching lecture schedules mapped to H4 timetable availability.
   - Interactive Candidate Pool Inspector filtering candidates across 3 verification tiers.
6. **Official Institutional Audit Report & PDF Export**:
   - Generates a signed, letterhead examination audit document for University Deans/Registrars with baseline-vs-recovered delta matrix, 8-point constraint proofs, and formal sign-off blocks.

---

## 🏛️ System Architecture

```
+-------------------------------------------------------------------------+
|                           CLIENT TIER (Browser)                         |
|  - Coordinator Console (index.html)     - Faculty Portal (faculty.html) |
|  - Candidate Pool Inspector             - Official PDF Audit Modal      |
+-------------------------------------------------------------------------+
                                    |
                                    | HTTP REST API (JSON)
                                    v
+-------------------------------------------------------------------------+
|                        APPLICATION TIER (FastAPI)                       |
|  - Authentication & RBAC (/auth/login)  - Timetable API (/schedule)     |
|  - Pre-Exam Reminders Broadcast         - Candidate Pool Evaluation     |
|  - Audit Snapshot Generation            - AI Copilot Natural Language   |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                      AGENTIC AI & RECOVERY TIER                         |
|                                                                         |
|   +-----------------------------------------------------------------+   |
|   |                      ExamSchedulerAgent                         |   |
|   |  PLAN -> VALIDATE -> DISRUPT -> DETECT -> REPAIR -> VERIFY      |   |
|   +-----------------------------------------------------------------+   |
|          |                 |                  |                |        |
|          v                 v                  v                v        |
|   SchedulePlanner   ScheduleValidator   ScheduleRepair   Explanation    |
|   (Resource Grid)   (H1-H8 Hard Rules)  (Min-Ripple)     (Gemini Dual)  |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                     DATA TIER (In-Memory Pydantic Store)                |
|  - Student Schema (Accessibility)        - Exam Schema (Cohorts)        |
|  - Room Schema (Capacities & Floors)     - Invigilator Schema (Schedule)|
+-------------------------------------------------------------------------+
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.12+ installed
- Git installed

### 2. Clone the Repository
```bash
git clone https://github.com/<your-username>/adaptive-exam-system.git
cd adaptive-exam-system
```

### 3. Create & Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install fastapi uvicorn pydantic
```

### 5. Launch Backend Server (Terminal 1)
```bash
python -m uvicorn backend.api:app --reload --port 8000
```
Backend will be live at: `http://127.0.0.1:8000` (Swagger UI docs at `http://127.0.0.1:8000/docs`)

### 6. Launch Frontend Server (Terminal 2)
```bash
cd frontend
python -m http.server 5500
```
Frontend will be live at: `http://127.0.0.1:5500`

---

## 🔑 Demo Credentials

### 1. Exam Operations Coordinator
- **URL**: `http://127.0.0.1:5500/index.html`
- **User ID**: `coordinator`
- **Password**: `admin123`

### 2. Individual Faculty Portal
- **URL**: `http://127.0.0.1:5500/faculty.html`
- **Primary Faculty Accounts**:
  - `I02` (Dr. Priya Sharma - ECE): `backup123` or `faculty123`
  - `I03` (Dr. Rajesh Verma - IT): `emergency123` or `faculty123`
  - `I01` (Dr. Ramesh Kumar - CSE): `test123` or `faculty123`
- **Extended Roster**: `I04` through `I12` (Password: `faculty123`)

---

## 🧪 Running Automated Tests

Run the complete test suite:
```bash
# Windows
$env:PYTHONIOENCODING="utf-8"
python -m unittest discover tests

# Linux / macOS
python3 -m unittest discover tests
```

---

## 👥 Project Team
* **Project**: Adaptive Exam Operations & Schedule Recovery System
* **Hackathon**: HACKSPRINT'26
* **Domain**: Education & Examination Operations
* **Theme**: Agentic AI

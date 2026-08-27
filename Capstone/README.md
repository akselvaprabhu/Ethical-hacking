# Intelligent API Attack Detection and Runtime Protection Framework

An end-to-end academic cybersecurity framework built to detect, score, and automatically block malicious REST API traffic at runtime using signature-based rules, machine-learning-based anomaly detection (Isolation Forest), dynamic risk scoring, and a dark-themed Security Operations Center (SOC) dashboard.

---

## Key Features

1. **Inline API Traffic Monitoring**: Captures client IP, HTTP method, endpoint, status code, execution latency, and authentication status in real time via Flask backend middleware.
2. **Dual-Engine Threat Detection**:
   - **Signature / Rule Engine**: Detects SQL Injection (SQLi), Cross-Site Scripting (XSS), Path Traversal, and Brute Force authentication failures.
   - **ML Anomaly Detection Engine**: Uses an unsupervised **Isolation Forest** model (`scikit-learn`) trained on API traffic features (request rates, 4xx/5xx status ratios, auth failure density, endpoint entropy).
3. **Dynamic Risk Scoring (0–100)**: Combines rule matches, ML anomaly probability scores, request frequencies, and failed login counts into risk categories (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
4. **Automated Runtime Protection**: Dynamically enforces IP blocking (`403 Forbidden`) and rate limiting when risk scores cross configurable thresholds ($\ge 65$).
5. **Dark Cybersecurity SOC Dashboard**: Built with React + Vite + TailwindCSS + Recharts. Provides live real-time auto-refresh telemetry (every 3 seconds), overview KPI cards, traffic time-series charts, threat distribution bar charts, security event audit logs, and an active firewall ban controller with manual unblock capabilities.
6. **Postman Demonstration Suite**: Includes a ready-to-import Postman Collection (`postman/API_Security_Framework_Demo.postman_collection.json`) covering 5 distinct live attack scenarios.

---

## Main System Architecture

```
User / Postman Client
         │
         ▼
[ Flask Traffic Monitoring Middleware ] ──────► IP Firewall Check (Blocked IP filter)
         │
         ▼
[ JWT Token Validation ]
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              Dual Attack Detection Engines              │
│  ├── Signature / Rule Engine (SQLi, XSS, Brute Force)   │
│  └── Scikit-Learn Isolation Forest ML Anomaly Engine    │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
              [ Dynamic Risk Scoring Engine (0-100) ]
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   Risk Score < 65                    Risk Score ≥ 65
        ALLOW                             BLOCK
  (Execute API Route)            (Enforce 15m IP Block & 403)
            │                                 │
            └────────────────┬────────────────┘
                             │
                             ▼
                 [ SQLite Audit Database ]
                             │
                             ▼
         [ React + Vite Admin SOC Security Dashboard ]
```

---

## Project Directory Structure

```
.
├── backend/
│   ├── app.py                   # Main Flask Application Entrypoint
│   ├── config.py                # Environment & Security Threshold Configuration
│   ├── database.py              # SQLAlchemy Database Setup
│   ├── requirements.txt         # Python Dependencies
│   ├── seed_data.py             # Database Auto-Seeding & Initial Telemetry
│   ├── models/                  # Database ORM Models (User, ApiLog, SecurityEvent, BlockedIp, Alert)
│   ├── routes/                  # API Endpoints (Auth, Demo Resources, Security Management)
│   ├── middleware/              # Real-Time Traffic Monitoring & Firewall Middleware
│   ├── detection/               # Signature Rules & Threat Detection Engine
│   ├── protection/              # IP Firewall & Sliding Window Rate Limiter
│   ├── ml/                      # Isolation Forest Dataset Generator, Trainer & Real-time Detector
│   └── utils/                   # JWT Helper & Risk Scorer Formula
├── frontend/
│   ├── package.json             # Node.js Dependencies (React, Vite, Tailwind, Recharts)
│   ├── vite.config.js           # Vite Server & Proxy Config
│   └── src/
│       ├── components/          # Navbar, StatCard, EventTable, BlockedIpTable, Charts
│       ├── pages/               # Dashboard, TrafficLogs, SecurityEvents, BlockedIps, Login
│       └── services/            # REST API Service Client
├── postman/
│   └── API_Security_Framework_Demo.postman_collection.json # Postman Test Suite
├── .env.example                 # Environment Variable Template
└── README.md                    # Project Documentation
```

---

## Getting Started & Local Installation

### Prerequisites
- Python 3.10 or higher
- Node.js v18 or higher & npm

### 1. Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed database and train ML model
python seed_data.py

# 4. Start Flask backend server (Runs on http-[#127.0.0.1:5000])
python app.py
```

### 2. Frontend Setup

```bash
# 1. Open a new terminal and navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start React + Vite development server (Runs on http-[#localhost:3000])
npm run dev
```

Open `http://localhost:3000` in your web browser to access the SOC Security Dashboard.

---

## Demonstration Guide (Postman Walkthrough)

Import `postman/API_Security_Framework_Demo.postman_collection.json` into Postman.

### Scenario 1: Normal API Access
1. Send `GET http://127.0.0.1:5000/api/products`.
2. **Result**: `200 OK`. Request logged in dashboard as `ALLOW` with Risk Score ~0.

### Scenario 2: Unauthorized Request
1. Send `GET http://127.0.0.1:5000/api/orders` without `Authorization` header.
2. **Result**: `401 Unauthorized`. Response details token requirement.

### Scenario 3: Brute Force Login Attack
1. Send multiple `POST http://127.0.0.1:5000/api/login` requests with invalid passwords (`"wrong_password"`).
2. **Result**: After 5 failed attempts, the IP is flagged for `Brute Force Attack`. The Risk Score jumps to $\ge 85$, the IP address is automatically added to `blocked_ips`, and subsequent requests return `403 Forbidden`. The dashboard updates live within 3 seconds.

### Scenario 4: SQL Injection Signature Match
1. Send `GET http://127.0.0.1:5000/api/products?search=' OR '1'='1`.
2. **Result**: Signature engine detects SQLi regex pattern, risk score escalates to 90, request is blocked with `403 Forbidden`, and a `CRITICAL` Security Event is recorded.

### Scenario 5: Unblocking an IP Address (Admin Override)
1. In Postman, send `POST http://127.0.0.1:5000/api/security/unblock-ip` with body `{"ip_address": "127.0.0.1"}` OR click **Unblock** on the React dashboard.
2. **Result**: The IP block is released immediately and normal API access resumes.

---

## Academic Viva Q&A Guide

**Q1: How does the framework differentiate between normal traffic spikes and malicious behavior?**  
*Answer*: It uses a hybrid detection model. Static rules catch known signature patterns (like SQLi or directory traversal), while the unsupervised Isolation Forest model analyzes statistical features (status error ratios, request frequency variance, auth failure density) to flag unusual deviations without relying solely on static thresholds.

**Q2: What algorithm is used for anomaly detection and why?**  
*Answer*: **Isolation Forest** (`scikit-learn`). Unlike distance-based algorithms, Isolation Forest explicitly isolates anomalies by randomly selecting a feature and splitting values. Since anomalies require fewer splits to isolate, they appear closer to the root of the trees, making it exceptionally fast and efficient for high-dimensional streaming data.

**Q3: How does runtime protection operate inline?**  
*Answer*: Through Flask `@app.before_request` middleware. Before any API route controller executes, the request metadata passes through the firewall check, rule engine, and ML model. If the resulting risk score crosses the threshold, the middleware immediately aborts execution and returns a `403 Forbidden` response, protecting underlying databases and business logic.

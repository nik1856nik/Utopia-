# Utopia — Smart Public Works Transparency & Municipal Operations Platform

Utopia is a full-stack civic transparency and municipal operations platform for Chennai. It provides an interactive **Google Maps-style** public works map, an **Amazon-style live project tracking pipeline**, construction hazard warnings (noise/dust timings), commute detour advisories intimating Google Maps, and an authenticated **Municipal Operations Portal** with the **DigSync** interdepartmental coordination engine.

---

## 🚀 Quick Start

### Option 1: Run with Docker Compose
```sh
docker compose up --build
```
- **Web App**: http://localhost:5173
- **API & Swagger Docs**: http://localhost:8000/docs
- **PostgreSQL / PostGIS**: localhost:5432 (credentials in `docker-compose.yml`)

### Option 2: Run Services Separately (Local Dev)

**Backend** (SQLite default or PostgreSQL):
```sh
cd backend
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload
```

**Frontend** (Vite + React + Leaflet):
```sh
cd frontend
npm install
npm run dev
```

*Note: Currently also serving live on port 8001 (API) and port 5174 (Web) for instant evaluation.*

---

## 🌟 Key Features & Implementation

### 1. 🗺️ Google Maps-Style Citizen Discovery
- **Full-bleed Map Canvas**: Interactive Leaflet map centered on Chennai with custom teardrop pins, animated active site pulses, and category badges.
- **Map & Satellite View**: Toggle between standard street map and high-resolution Esri Satellite imagery.
- **Google Maps Floating Search Bar**:
  - Search by 6-digit PIN code (`600017`, `600004`, `600020`, `600042`, etc.), locality, road name, or project ID.
  - Quick-search chips for Chennai areas: *600017 T. Nagar*, *600004 Mylapore*, *600020 Adyar*, *600042 Velachery*, etc.
  - Category filters: *All Works*, *Drainage & Stormwater*, *Metro Water*, *Roads & Paving*, *Electricity*, *Telecom Fibre*, *Delayed*, *Road Closures*.
- **Google Maps Place Sheet**: Selecting any project smoothly pans the map and opens the slide-in inspection sheet.

### 2. 📦 Amazon-Style Live Project Tracking
Upon selecting a project and scrolling down:
- **7-Stage Milestone Delivery Pipeline**:
  1. *Sanction & DPR Published*
  2. *Tender & Site Mobilisation*
  3. *Utility Shifting & Excavation*
  4. *Core Conduit / Pipe Laying*
  5. *Quality & Compaction Audit*
  6. *Road Surface Restoration & Asphalting*
  7. *Commissioned & Reopened*
- **Visual Tracker**: Shows completed stages with green checkmarks, currently active stage with pulsing radar indicator, and progress bar.
- **Delay Transparency**: If behind schedule, displays an alert with the published reason for delay, official mitigation plan, and original vs revised completion dates.

### 3. ⚠️ Construction Hazard Warnings & Timings
- **Noise Warnings**: Permitted heavy work window (e.g., `22:00 – 04:00`, acoustic curtains mounted, decibel management).
- **Dust Advisories**: Permitted excavation window (e.g., `09:00 – 14:00`, water mist cannons active).
- **Advance Intimation**: Validates whether residents in the ward were given advance 48-hour notice.

### 4. 🚗 Commuter Advisory & Google Maps Broadcast
- Real-time road restriction and lane blockage status.
- **"Intimated to Google Maps & Chennai Traffic Police"**: Live dispatch indicator.
- Recommended detour route for motorists and pedestrians.

### 5. 👷 Work Handler & Contractor Contacts
- **Site Executive Engineer**: Name, phone number, official email, and municipal zone.
- **Executing Contractor**: Agency name and site supervisor contact number.
- **24/7 Grievance Helpline**: Greater Chennai Corporation 1913.

### 6. 💬 Citizen Feedback, Q&A & Complaints
- Public Q&A thread with official answers from municipal site engineers.
- "Ask a Question" regarding project lags and timelines.
- "Report Issue" modal: Citizens can report noise, dust, missing barricades, or water disruptions with instant reference ID generation (`CGI-XXXX`).

---

## 🔐 Municipal Operations Portal (`/admin`)

The Municipal View is protected by an **Official Authentication Gate** branded with the Greater Chennai Corporation seal.

### Demo Officer Accounts:
| Role / Designation | Email | Password | Department |
| :--- | :--- | :--- | :--- |
| **GCC Super Admin** | `admin@gcc.gov.in` | `admin123` | Greater Chennai Corporation |
| **Metro Water Nodal Officer** | `water@metrowater.tn.gov.in` | `water123` | Chennai Metro Water |
| **Chief Roads Engineer** | `roads@gcc.gov.in` | `roads123` | GCC Roads & Bridges |
| **TANGEDCO Utility Lead** | `power@tangedco.gov.in` | `power123` | TANGEDCO (Electricity) |

*The login screen includes quick one-click buttons to log in as any of the above officers for effortless evaluation.*

### Authenticated Municipal Operations Features:
- **Consolidated Citywide Dashboard**: Live KPIs for total works, active sites, lagging projects, citizen grievances, and DigSync overlaps.
- **DigSync Interdepartmental Coordination Engine**:
  - Automatically flags spatial overlaps (< 1.5 km) and overlapping construction windows between different departments.
  - Highlights collision type (e.g., *Excavation Collision* between Metro Water and Chennai Fibre).
  - Action modal to propose joint trenching or reschedule excavation before road restoration.
- **Public Works Register & Milestone Manager**:
  - Interactive table with departmental filtering.
  - Officer modal to update progress %, advance Amazon milestone steps (1–7), log delay explanations, update noise/dust permit hours, and toggle Google Maps navigation broadcasts.
- **Citizen Grievance & Q&A Triage**:
  - Filter incoming reports by status (`Submitted`, `In Progress`, `Resolved`).
  - Officer response composer to dispatch official replies directly to citizens.

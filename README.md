# SpaceX Analytics Solution — Technical Document
**Author:** Marcos Sanchez
**Latest Updates:** Extended filters, D3.js visualizations, Improved resilience

This version meets the requirements of the QuadSci Full Stack Engineer Technical Exercise.

---

## 1) Goal
- Get data from the SpaceX public API
- Transform data on the **server** in real time (filters + pagination + metrics)
- Expose REST API (FastAPI) with QuadSci-required endpoints
- Build Vue 3 web app with D3.js visualizations

---

## 2) Key Improvements (QuadSci Compliance)
### Backend
- ✅ **New filters**: `success` for launches
- ✅ **Starlink normalization**: `inclination_deg` field added
- ✅ **Retry mechanism**: Exponential backoff (3 attempts)
- ✅ **Enhanced error handling**: Cache fallback on errors

### Frontend
- ✅ **D3.js integration**: Rocket specs comparison chart
- ✅ **Dynamic filtering**: UI connects to backend filters
- ✅ **Real data only**: Removed Starlink demo satellites
- ✅ **ENV configuration**: `VITE_BACKEND_URL` support

---

## 3) What is inside
### Backend (FastAPI)
- **Endpoints**:
  - `GET /api/dashboard` — Totals and KPI metrics
  - `GET /api/rockets` — Filter `active`; pagination
  - `GET /api/launches` — Filters `year`, `success`; returns `stats.success_rate`
  - `GET /api/starlink` — Filters `altitude_min`, `inclination_min`; normalized data
- **Service layer**:
  - Async HTTP with **httpx**
  - **TTLCache** per endpoint (5 min)
  - **Retry mechanism** with exponential backoff (`tenacity`)
  - Error handling with cache fallback

### Frontend (Vue 3 + Vite + D3.js)
- **Base URL**: Configurable via `.env` (`VITE_BACKEND_URL`)
- **Composable** `useSpaceX`:
  - Supports query parameters for all endpoints
  - Loading states and error handling
  - Methods: `fetchRockets(params)`, `fetchLaunches(params)`, `fetchStarlink(params)`
- **Data contract**:
  - Rockets: `height` (m), `mass` (kg) for D3 charts
  - Starlink: Standardized `inclination_deg` from backend
  - Launches: Real-time success rate metrics

### Key Components & Views
- `DashboardView.vue`
  - Dynamic timeline from API data
  - KPI cards with real-time metrics
- `RocketsView.vue`
  - **D3.js bar chart** comparing height/mass
  - Server-side `active` filter
  - Client-side name search
- `StarlinkView.vue`
  - Three.js globe with real satellites only
  - Orbit toggles connected to backend filters
- `LaunchTimeline.vue`
  - Dynamic chart using `/api/launches` data

---

## 4) API details (QuadSci Compliance)

### `/api/rockets`
```json
{
  "data": [
    {
      "id": "5e9d0d95eda69973a809d1ec",
      "name": "Falcon 9",
      "active": true,
      "height": 70.0,
      "mass": 549054,
      "cost": 50000000,
      "success_rate": 94,
      "first_flight": "2010-06-04"
    }
  ],
  "pagination": { "total": 4, "page": 1, "per_page": 10, "total_pages": 1 }
}
```

### `/api/launches` (Updated)
**New params**: `success` (bool)
```json
{
  "data": [ /* launch objects */ ],
  "pagination": { "total": 24, "page": 1, "per_page": 50, "total_pages": 1 },
  "stats": { "success_rate": 87.5 }
}
```

### `/api/starlink` (Updated)
**Normalized field**: `inclination_deg`
```json
{
  "data": [
    {
      "id": "5eed7715096e5900069857d1",
      "inclination_deg": 53.0
    }
  ]
}
```

---

## 5) Data Visualization (QuadSci Compliance)
| View | Visualization | Library | Data Source |
|------|---------------|---------|-------------|
| **Dashboard** | Launch timeline | D3.js | `/api/launches` |
| **Rockets** | Height/mass comparison | D3.js | `/api/rockets` |
| **Starlink** | Satellite globe | Three.js | `/api/starlink` |

---

## 6) How to run
### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate    # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
echo "VITE_BACKEND_URL=http://localhost:8000" > .env
npm run dev
```

---

## 7) Testing Endpoints
```bash
# Get successful launches in 2023
curl "http://localhost:8000/api/launches?year=2023&success=true"

# Get active rockets
curl "http://localhost:8000/api/rockets?active=true"

# Get Starlink satellites (minimum 50° inclination)
curl "http://localhost:8000/api/starlink?inclination_min=50"
```

---

## 8) QuadSci Requirements Coverage
| Requirement | Status | Details |
|-------------|--------|---------|
| **Backend filters** | ✅ | Added `success` for launches |
| **D3.js visualizations** | ✅ | Rocket comparison chart |
| **Real-time data** | ✅ | All views use API data |
| **Starlink normalization** | ✅ | `inclination_deg` field |
| **Error resilience** | ✅ | Retry + cache fallback |
| **ENV config** | ✅ | `VITE_BACKEND_URL` support |

---

## 9) Roadmap
```mermaid
graph LR
A[Current] --> B[Add sorting]
A --> C[Starlink metrics]
A --> D[Enhanced D3 tooltips]
C --> E[Altitude averages]
C --> F[Decayed count]
```

---

## 10) Notes for QuadSci Review Panel
1. All required endpoints implemented
2. D3.js visualizations integrated for rocket comparison
3. Retry mechanism with exponential backoff
4. UI filters connected to backend
5. Starlink data normalized (no demo data)
6. Timeline panel now uses live data

---

## Design Decisions
- **Three.js for Starlink**: Native, high-performance 3D rendering for interactive globes. D3.js is primarily 2D.
- **TTLCache (in-memory)**: Simplifies local review without additional infrastructure. In production, Redis or similar could be used.
- **Tenacity retries**: Exponential backoff increases resilience against upstream API hiccups.
- **Server-side normalization**: Ensures consistent naming (`inclination_deg`, `altitude_km`) across frontend and backend.

## Challenges & Solutions
- **Starlink field variability**: Some items lacked consistent fields.  
  **Solution**: Normalize in service layer to ensure all have `inclination_deg` and `altitude_km`.
- **Intermittent upstream failures**: Caused occasional API errors.  
  **Solution**: Implemented `tenacity` retries and cache fallback.
- **Timeline drift**: Static data became outdated.  
  **Solution**: Drive timeline from `/api/launches` real-time data.

## Screenshots (Reviewer Friendly)
Include these images in `frontend/public/screenshots/`:
- `dashboard.png`
- `rockets.png`
- `starlink.png`

Example in README:
```markdown
### Visual Evidence
![Dashboard](frontend/public/screenshots/dashboard.png)
![Rockets](frontend/public/screenshots/rockets.png)
![Starlink](frontend/public/screenshots/starlink.png)
```

## QuadSci Notebook (Executable)
A Jupyter Notebook (`spacex_quadsci_notebook.ipynb`) is provided with Markdown explanations and Python code cells to call all API endpoints.  
Requirements to run:
- Backend running locally at `http://localhost:8000`

---

## Reviewer Checklist
| Requirement | Status |
|-------------|--------|
| Architecture explanation (backend/frontend) | ✅ |
| Endpoints details (request/response examples) | ✅ |
| Config and how to run | ✅ |
| QuadSci coverage | ✅ |
| **Screenshots** | ⬜ |
| **Design Decisions** | ✅ |
| **Challenges & Solutions** | ✅ |
| **Executable Notebook** | ✅ |

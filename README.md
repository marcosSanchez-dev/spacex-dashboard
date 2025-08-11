# SpaceX Analytics Solution — Technical Document
**Author:** Marcos Sanchez • **Date:** 2025-08-11 (UTC)

This version matches the **current code** (FastAPI + Vue 3). It uses simple English.

---

## 1) Goal
- Get data from the SpaceX public API.
- Transform data on the **server** in real time (basic filters + pagination).
- Expose a small REST API (FastAPI).
- Build a web app (Vue 3) with D3/Three visualizations.

---

## 2) What is inside
### Backend (FastAPI)
- Endpoints:
  - `GET /api/dashboard` — totals and small counters (rockets, launches, starlink).
  - `GET /api/rockets` — filter `active`; pagination; mapped fields for charts.
  - `GET /api/launches` — filter `year`; pagination; returns `stats.success_rate`.
  - `GET /api/starlink` — filters: `altitude_min`, `inclination_min`; pagination.
- Service layer:
  - Async HTTP with **httpx**
  - **TTLCache** per endpoint (5 min)
  - Simple error handling (no retries / no cache fallback on error)

### Frontend (Vue 3 + Vite)
- **Base URL**: the app points to `http://localhost:8000` (hardcoded in `src/composables/useSpaceX.ts`).
- **Composable** `useSpaceX`:
  - Axios-based `GET` helper `fetchData` with `isLoading` and `error` states.
  - Helpers: `fetchRockets()` and `fetchStarlink()`.
  - Does **not** pass query params to the backend (UI filters are client-side only).
- **Data contract (client)**:
  - Rockets: expects numbers for `height` (m) and `mass` (kg) as returned by the backend mapper.
  - Starlink: UI components use `altitude_km` and a **client field** `inclination_deg` (for demo items). Real API data coming from the backend provides `inclination` (not `inclination_deg`); orbit toggles are therefore **client-only** and rely on demo data for consistent visuals.

### Key Components & Views (actual behavior)
- `DashboardView.vue`
  - Loads `/api/dashboard` for KPI cards (totals).
  - Loads rockets and starlink via composable (no query params).
  - **LaunchTimeline**: uses internal (static) historical dataset in the view for yearly breakdown (not computed from `/api/launches`).
  - **StarlinkGlobe**: shows satellites from API **or** demo fallback; `highlightOrbit` is not set (shows all).
- `RocketsView.vue`
  - Fetches `/api/rockets` (no params) and offers **client-side** text filter by name.
  - Renders `Rocket3DBarChart` with `height`/`mass` numeric fields from the backend mapper.
  - Displays a **LaunchTimeline** panel (visual only; not tied to `/api/launches`).
- `StarlinkView.vue`
  - Implements its **own** Three.js globe (not the shared `StarlinkGlobe`).
  - Calls `/api/starlink` **without filters**; if empty, uses **150 demo satellites**; if there is data, it **tops up** with demo items to keep a stable count (~150) for consistent visuals.
  - Orbit toggles (**ALL / POLAR / GEO**) are **client-side only** and depend on `inclination_deg` (present in demo objects). Real API items are displayed but not normalized to `inclination_deg`.

- Assets
  - Earth textures under `public/textures/earth/{color.jpg,bump.jpg,specular.jpg,clouds.jpg}`.
  - Components load textures with relative paths like `textures/earth/color.jpg` (Vite serves them from `/`).

---

## 3) Coherence with the code (confirmed)
- **Dashboard**: totals from `/api/dashboard`; timeline is **frontend-only** (static).
- **Rockets**: `active` filter exists on the API, but the view does not send it; filtering by name is client-side.
- **Launches**: API supports only `year`; no server sorting; the timeline in UI does not depend on this API.
- **Starlink**: API supports only `altitude_min` and `inclination_min`; the UI does **not** pass these; the 3D globes use demo data to ensure stable visuals and client-only orbit toggles.

---

## 4) Optional roadmap (future work)
### Backend
| Feature in doc | Current code | Next step (optional) |
|---|---|---|
| `/launches` filter `success` | Not implemented | Add query param and filter |
| `/launches` sort by date | Not implemented | Add `sort`/`dir` |
| `/starlink` `max_altitude`, `max_inclination`, `decayed` | Not implemented | Add filters |
| `/starlink` metrics (`altitude_avg`, `decayed_count`) | Not implemented | Compute after filtering |
| Robust `spaceTrack` checks | Basic | Safe access in all endpoints |
| Retries + cache fallback | No | Add retry/backoff and use cache as fallback |

### Frontend
| Feature in doc | Current code | Next step (optional) |
|---|---|---|
| `.env` `VITE_BACKEND_URL` | Hardcoded URL | Read from `.env` |
| Pass query params from UI | Not supported | Add `params` in composable |
| Starlink inclination naming | `inclination` (API) vs `inclination_deg` (UI demo) | Normalize on client/server |
| Launch timeline data | Static in view | Optionally derive from `/api/launches` |

---

## 5) API details (current)

### `/api/dashboard`
**Response (example)**
```json
{
  "rockets": { "total": 4, "active": 3 },
  "launches": { "total": 250, "successful": 230, "upcoming": 3 },
  "starlink": { "total": 6000, "deployed": 5980 }
}
```
**Notes**: `deployed` = `spaceTrack.DECAY_DATE` is `null` if present (simple check).

---

### `/api/rockets`
**Query params**:  
- `active` (bool, optional)  
- `page` (default 1), `limit` (default 10, 1–50)

**Response (example)**
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

---

### `/api/launches`
**Query params**:  
- `year` (int, optional)  
- `page` (default 1), `limit` (default 50, 1–100)

**Response (example)**
```json
{
  "data": [ /* raw launch objects from SpaceX */ ],
  "pagination": { "total": 24, "page": 1, "per_page": 50, "total_pages": 1 },
  "stats": { "success_rate": 87.5 }
}
```
**Notes**: Only `year` filter. No `success` filter. No date sorting.

---

### `/api/starlink`
**Query params**:  
- `altitude_min` (km), `inclination_min` (degrees)  
- `page` (default 1), `limit` (default 50, 1–100)

**Response (example)**
```json
{
  "data": [
    {
      "id": "5eed7715096e5900069857d1",
      "name": "OBJECT_NAME or Unknown",
      "launch_date": "YYYY-MM-DD",
      "longitude": -97.0,
      "latitude": 19.5,
      "altitude_km": 550.2,
      "velocity_kms": 7.6,
      "inclination": 53.0,
      "decayed": false
    }
  ],
  "pagination": { "total": 123, "page": 1, "per_page": 50, "total_pages": 3 }
}
```
**Notes (UI)**: The UI keeps a stable count (~150) by adding **demo** satellites when needed. Orbit toggles (POLAR/GEO) are client-side and rely on demo data’s `inclination_deg`. The UI currently does not pass server filters.

---

## 6) Data flow & transforms (current)
- Fetch from SpaceX API (with 5-minute TTL cache).
- Apply **basic filters** on server:
  - Rockets: `active`
  - Launches: `year`
  - Starlink: `altitude_min`, `inclination_min`
- Paginate results.
- Compute **launches success rate** only (no other metrics at this time).
- **Frontend**:
  - KPIs from `/api/dashboard`; timeline uses static dataset in the view.
  - Starlink 3D globes: display API data, **augmented with demo** to ensure consistent visuals and client-only orbit toggles.

---

## 7) Charts (current status)
- **Dashboard**: KPI cards (API), launch timeline (static), rocket 3D bars (API), Starlink globe (API + demo).
- **Rockets view**: client text filter + 3D bar chart (API mapped fields).
- **Starlink view**: custom Three.js globe with orbit toggles (client-only; API + demo).

---

## 8) How to run
### Backend
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# Docs: http://localhost:8000/api/docs
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# App: http://localhost:5173
# Note: the app uses http://localhost:8000 as backend (hardcoded in useSpaceX.ts)
```

---

## 9) Quick test (cURL)
```bash
# Starlink with available server filters (UI does not send them)
curl "http://localhost:8000/api/starlink?altitude_min=500&inclination_min=50&page=1&limit=20"

# Rockets (active only)
curl "http://localhost:8000/api/rockets?active=true&page=1&limit=10"

# Launches (2020; no sort, no success filter)
curl "http://localhost:8000/api/launches?year=2020&page=1&limit=50"

# Dashboard
curl "http://localhost:8000/api/dashboard"
```

---

## 10) Notes for AI/ML
- Reproducible runs via **code + API** (no notebooks).
- Current server supports **basic slices**; UI shows static timeline and demo-augmented Starlink visualization for stable UX.
- Easy to extend later (filters, metrics, retries, environment config).

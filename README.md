# SpaceX Analytics Solution — Technical Document 
**Author:** Marcos Sanchez • **Date:** 2025-08-11 (UTC)

> This version removes the notebook and explains **real‑time processing in the backend**.  
> It also aligns the **Starlink API filters** and the **Vue composable**.

---

## 1) Goal
- Get data from the SpaceX public API.
- Clean and transform data **on the server** in real time.
- Expose a small REST API (FastAPI) with filters and pagination.
- Build a simple web app (Vue 3 + D3.js / Three.js) to show charts.

---

## 2) What is inside (updated)
### Backend (FastAPI)
Endpoints:
- `GET /api/dashboard` — key numbers and small summaries.
- `GET /api/rockets` — rocket info. Filters: `active`; supports pagination.
- `GET /api/launches` — filters: `year`, `success`; sort by date; pagination.
- `GET /api/starlink` — **real‑time filters and metrics**:
  - Filters: `min_altitude`, `max_altitude`, `min_inclination`, `max_inclination`, `decayed`
  - Pagination: `page`, `limit`
  - Metrics in response (computed on the **filtered** set):
    - `altitude_min`, `altitude_max`, `altitude_avg`
    - `decayed_count`

Service layer:
- Async HTTP calls with **httpx**
- **TTLCache** per endpoint (5 minutes)
- Short **auto‑retries** and **fallback to cache** on errors
- Clear error messages (HTTP 4xx/5xx)

### Frontend (Vue 3 + Vite)
- Charts with **D3.js** and **Three.js**.
- **useSpaceX composable**:
  - Uses env: `VITE_BACKEND_URL` (no hardcoded URLs)
  - Allows **query params** (filters + pagination) for all endpoints
  - Basic TypeScript interfaces for responses

### Vue Components (key ones)
- `LaunchTimeline` — timeline of launches per year.
- `SuccessPie` — success vs fail pie chart.
- `Rocket3DBarChart` — 3D bar chart for rocket size.
- `StarlinkGlobe` — interactive 3D globe.
- `AnimatedCounter` — animated KPIs.

---

## 3) Why these choices (expanded)
- **Real‑time server processing:** flexible filters and simple ops (no pre‑ETL step).
- **FastAPI + httpx:** async, fast, with auto docs.
- **TTL cache (5 min):** fewer calls to SpaceX; faster answers.
- **Three.js:** better 3D experience; preload textures for speed.
- **D3.js:** full control of charts; Chart.js is a simple fallback.
- **Env‑driven config:** `VITE_BACKEND_URL` for easy local/prod switch.
- **Graceful fallback:** demo data or cached data if the API fails.

---

## 4) How to run
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
# .env --> VITE_BACKEND_URL=http://localhost:8000
```

> Note: We **do not** depend on a notebook now.

---

## 5) Data flow & real‑time transforms
- **Normalize fields**: e.g., `height_km` → `altitude_km`; handle missing `spaceTrack`.
- **Apply filters**:
  - Altitude: `min_altitude` / `max_altitude`
  - Inclination: `min_inclination` / `max_inclination`
  - `decayed`: include only decayed or only active
- **Paginate** results: `page`, `limit`.
- **Compute metrics** on the **filtered** list:
  - `altitude_min`, `altitude_max`, `altitude_avg`
  - `decayed_count`

---

## 6) Charts idea (updated)
- **Dashboard**:
  - **Launch timeline** (timeline chart)
  - **Success rate** (pie chart)
  - **Rocket fleet preview** (3D bar chart)
  - **Starlink preview** (3D globe, no filters here)
- **Rockets view**: compare height/mass (bar or 3D bar)
- **Launches view**: timeline and success by year
- **Starlink view**: 3D globe + filters (orbit type, altitude, inclination)

---

## 7) Quick test (cURL)
```bash
# Starlink with all filters and metrics
curl "http://localhost:8000/api/starlink?min_altitude=500&max_altitude=600&min_inclination=50&max_inclination=60&decayed=false&page=1&limit=20"

# Rockets (active only)
curl "http://localhost:8000/api/rockets?active=true&page=1&limit=10"

# Launches (2020; desc)
curl "http://localhost:8000/api/launches?year=2020&sort=date&dir=desc&page=1&limit=50"
```

---

## 8) Panel walkthrough (90 min, updated)
1) Context and goal (5 min)  
2) Backend live demo (25 min): `/api/docs`, filters, pagination, cache  
3) **Backend transforms** (15 min): real‑time metrics, why no notebook  
4) Frontend (25 min): views, charts, loading, error states  
5) Q&A (20 min): next steps (Redis, auth, tests)

---

## 9) Notes for AI/ML
- Reproducible results come from code + API, not from a notebook.
- Real‑time filters allow flexible slices for analysis.
- Easy to extend with more features (e.g., 5‑year moving success rate).

---

## 10) Coherence summary
### `backend/api/starlink.py`
- **Add** missing filters: `max_altitude`, `max_inclination`, `decayed`.
- **Add** metrics in response (on filtered set): `altitude_min`, `altitude_max`, `altitude_avg`, `decayed_count`.
- **Careful**: `spaceTrack` may be missing; check for keys.

### `frontend/src/composables/useSpaceX.ts`
- **Use** `VITE_BACKEND_URL` (no hardcoded host).
- **Allow** query params in all fetch helpers.
- **Add** basic interfaces for responses (no `any[]`).

---

## 11) Implementation checklist
### Backend
- [ ] Add `max_altitude`, `max_inclination`, `decayed` filters
- [ ] Compute metrics on filtered list
- [ ] Keep TTL cache + retries + error messages

### Frontend
- [ ] Read `VITE_BACKEND_URL` from `.env`
- [ ] Pass params from UI to composable
- [ ] Update globe view to use new filters

---

## 12) Files for next review
- `backend/api/starlink.py`
- `frontend/src/composables/useSpaceX.ts`
- `frontend/src/components/StarlinkGlobe.vue`

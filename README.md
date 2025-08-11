# SpaceX Analytics Solution — Technical Document (B1 English, v6)
**Author:** Marcos Sanchez • **Date:** 2025-08-11 (UTC)

This version **integrates your final edits**. It keeps simple English and matches the real code.

---

## 1) Goal
- Get data from the SpaceX public API.
- Clean and transform data **on the server** in real time.
- Expose a small REST API (FastAPI) with filters and pagination.
- Build a web app (Vue 3 + D3.js / Three.js) to show charts.

---

## 2) What is inside
### Backend (FastAPI)
- Endpoints:
  - `GET /api/dashboard` — key numbers and small summaries.
  - `GET /api/rockets` — filter `active`; pagination.
  - `GET /api/launches` — filters: `year`, `success`; sort by date; pagination.
  - `GET /api/starlink` — **real‑time filters and metrics** (see details below).
- Service layer:
  - Async HTTP with **httpx**
  - **TTLCache** per endpoint (5 min)
  - Short retries + fallback to cache
  - Clear HTTP errors

### Frontend (Vue 3 + Vite)
- Charts with **D3.js** and **Three.js**
- **Composable** `useSpaceX` (central fetch, loading, error)
- Uses `.env` → **`VITE_BACKEND_URL`** (no hardcoded URLs)
- Accepts query params for all endpoints
- Simple TypeScript types for responses

### Key Components
- `LaunchTimeline` — timeline of launches
- `SuccessPie` — success vs fail pie
- `Rocket3DBarChart` — 3D bars for rocket size
- `StarlinkGlobe` — 3D globe
- `AnimatedCounter` — KPI cards

---

## 3) Coherence with the code (confirmed)
- **Backend**: starlink endpoint does **normalize fields** (`height_km → altitude_km`), handles **missing `spaceTrack`**, applies **basic filters** and **pagination**.
- **Frontend**: composables + components match the doc; **Three.js** for 3D is correct.
- **Notebook**: removed; the system now uses **real‑time** transforms in the backend.

---

## 4) Pending items (implementation gaps)
### Backend: `backend/api/starlink.py`
| Document | Current code | Required action |
|---|---|---|
| Filters: `max_altitude`, `max_inclination`, `decayed` | Only `min_*` | Add missing filters |
| Metrics: `altitude_avg`, `decayed_count` | Not computed | Add real‑time metrics |
| Robust `spaceTrack` | Basic `get(...)` | Improve safe checks |

**Code hints**
```python
# inside starlink.py (after filtering)
alts = [s.get("height_km", s.get("altitude_km")) for s in filtered if s.get("height_km") or s.get("altitude_km")]
alts = [float(a) for a in alts if a is not None]
altitude_avg = (sum(alts) / len(alts)) if alts else None
decayed_count = sum(1 for s in filtered if (s.get("spaceTrack") or {}).get("DECAYED") or (s.get("spaceTrack") or {}).get("DECAY_DATE"))
```

### Frontend: `frontend/src/composables/useSpaceX.ts`
| Document | Current code | Required action |
|---|---|---|
| Use `VITE_BACKEND_URL` | Hardcoded `localhost:8000` | Use env var |
| Support query params | Not supported | Add `params` object in `fetchData` |
| Strong typing | Uses `any[]` | Add basic TypeScript interfaces |

**Code hints**
```ts
const BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

async function fetchData<T>(endpoint: string, params: Record<string, any> = {}): Promise<T> {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => (v ?? v === 0) && qs.append(k, String(v)));
  const url = `${BASE_URL}${endpoint}${qs.toString() ? `?${qs.toString()}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return (await res.json()) as T;
}
```

---

## 5) API details: `/api/starlink` (server‑side, real‑time)
**Query params**
- `page`, `limit`
- `min_altitude`, `max_altitude`
- `min_inclination`, `max_inclination`
- `decayed` (true/false)

**Response (example)**
```json
{
  "data": [ ... ],
  "pagination": { "total": 123, "page": 1, "per_page": 20, "total_pages": 7 },
  "metrics": {
    "altitude_min": 545.1,
    "altitude_max": 560.3,
    "altitude_avg": 552.7,
    "decayed_count": 2
  }
}
```

**Notes**
- Field normalize: `height_km → altitude_km`
- `spaceTrack` may be missing; do safe checks

---

## 6) Data flow & transforms (real‑time)
- Normalize fields
- Apply filters
- Paginate results
- Compute metrics on the **filtered** list

---

## 7) Charts idea
- **Dashboard**: launch timeline, success rate (pie), rocket fleet preview (3D bars), **Starlink preview (3D globe, data from filtered backend)**.
- **Rockets view**: compare height/mass (bar or 3D bar).
- **Launches view**: timeline and success by year.
- **Starlink view**: 3D globe + filters (orbit type, altitude, inclination).

---

## 8) How to run
### Backend
```bash
cd backend
python -m venv venv
# Windows: venv\\Scripts\\activate
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

---

## 9) Quick test (cURL)
```bash
# Starlink with all filters and metrics
curl "http://localhost:8000/api/starlink?min_altitude=500&max_altitude=600&min_inclination=50&max_inclination=60&decayed=false&page=1&limit=20"

# Rockets (active only)
curl "http://localhost:8000/api/rockets?active=true&page=1&limit=10"

# Launches (2020; desc)
curl "http://localhost:8000/api/launches?year=2020&sort=date&dir=desc&page=1&limit=50"
```

---

## 10) Implementation checklist
### Backend
- [ ] Add `max_altitude`, `max_inclination`, `decayed` filters
- [ ] Compute `altitude_avg`, `decayed_count`
- [ ] Keep TTL cache + retries + clear errors

### Frontend
- [ ] Read base URL from `.env`
- [ ] Pass params from UI to composable
- [ ] Add basic interfaces (remove `any[]`)

---

## 11) Notes for AI/ML
- We use **code + API** for reproducible runs (no notebook).
- Real‑time filters allow flexible slices for analysis.
- Easy to extend (e.g., 5‑year moving success rate later).


# SpaceX Analytics Solution — Technical Document (B1 English, v6.1)

**Author:** Marcos Sanchez • **Date:** 2025-08-11 (UTC)

This version matches the **current code** (FastAPI + Vue 3). It uses simple English.

---

## 1) Goal

* Get data from the SpaceX public API.
* Transform data **on the server** in real time (basic filters and pagination).
* Expose a small REST API (FastAPI).
* Build a web app (Vue 3) with D3/Three components.

---

## 2) What is inside

### Backend (FastAPI)

* Endpoints:

  * `GET /api/dashboard` — totals and small counters (rockets, launches, starlink).
  * `GET /api/rockets` — filter `active`; pagination; mapped fields for charts.
  * `GET /api/launches` — filter `year`; pagination; returns `stats.success_rate`.
  * `GET /api/starlink` — filters: `altitude_min`, `inclination_min`; pagination.
* Service layer:

  * Async HTTP with **httpx**
  * **TTLCache** per endpoint (5 min)
  * Simple error handling (no retries / no cache fallback on error)

### Frontend (Vue 3 + Vite)

* Charts with **D3.js** and **Three.js**
* **Composable** `useSpaceX` for fetch, loading and error
* Uses **hardcoded base URL** `http://localhost:8000` (not `.env`)
* Composable does **not** accept query params (filters are not passed from UI)
* Uses loose typing (`any[]` for arrays)

### Key Components (conceptual)

* `LaunchTimeline` — timeline of launches (frontend only)
* `SuccessPie` — success vs fail pie (frontend only)
* `Rocket3DBarChart` — 3D bars for rocket size
* `StarlinkGlobe` — 3D globe
* `AnimatedCounter` — KPI cards

---

## 3) Coherence with the code (confirmed)

* **Dashboard**: totals are computed with simple counters. “Deployed” for Starlink means `spaceTrack.DECAY_DATE is None` (no advanced checks).
* **Rockets**: supports `active`, returns mapped fields (`height.meters`, `mass.kg`, etc.) and pagination.
* **Launches**: supports only `year` filter; returns `stats.success_rate`; **no** sort by date; **no** `success` filter.
* **Starlink**: supports only `altitude_min`, `inclination_min`; returns paginated list; **no** metrics; **no** `max_*` or `decayed` filter.

---

## 4) Optional roadmap (future work)

### Backend

| Feature in doc                                           | Current code    | Next step (optional)                        |
| -------------------------------------------------------- | --------------- | ------------------------------------------- |
| `/launches` filter `success`                             | Not implemented | Add query param and filter                  |
| `/launches` sort by date                                 | Not implemented | Add `sort`/`dir`                            |
| `/starlink` `max_altitude`, `max_inclination`, `decayed` | Not implemented | Add filters                                 |
| `/starlink` metrics (`altitude_avg`, `decayed_count`)    | Not implemented | Compute after filtering                     |
| Robust `spaceTrack` checks                               | Basic           | Safe access in all endpoints                |
| Retries + cache fallback                                 | No              | Add retry/backoff and use cache as fallback |

### Frontend

| Feature in doc            | Current code  | Next step (optional)       |
| ------------------------- | ------------- | -------------------------- |
| `.env` `VITE_BACKEND_URL` | Hardcoded URL | Read from `.env`           |
| Pass query params from UI | Not supported | Add `params` in composable |
| Strong typing             | `any[]`       | Add basic interfaces       |

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

**Notes**: Uses simple counters. `deployed` = `spaceTrack.DECAY_DATE` is `null` if present.

---

### `/api/rockets`

**Query params**:

* `active` (bool, optional)
* `page` (default 1), `limit` (default 10, 1–50)

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

* `year` (int, optional)
* `page` (default 1), `limit` (default 50, 1–100)

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

* `altitude_min` (km), `inclination_min` (degrees)
* `page` (default 1), `limit` (default 50, 1–100)

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

**Notes**: No `max_*` filters, no `decayed` filter, no metrics.

---

## 6) Data flow & transforms (current)

* Fetch from SpaceX API (with 5-minute TTL cache).
* Apply **basic filters** (`rockets: active`, `launches: year`, `starlink: altitude_min/inclination_min`).
* Paginate results.
* Compute **launches success rate** only (no other metrics at this time).

---

## 7) Charts idea (current status)

* **Dashboard**: launch timeline (frontend only), success rate pie, rocket 3D bars, Starlink globe preview.
  *(Starlink filters/metrics shown in UI should match the current backend: only `altitude_min` and `inclination_min`.)*
* **Rockets view**: compare height/mass (bar or 3D bar) using mapped fields.
* **Launches view**: show raw data by year and success rate.
* **Starlink view**: 3D globe + basic filters (min altitude / min inclination).

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
# Starlink with available filters
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

* Reproducible runs via **code + API** (no notebooks).
* Current server supports **basic slices** for analysis (year on launches; min filters on Starlink).
* Easy to extend later (filters, metrics, retries, environment config).
```

Este archivo:
- Está completamente en formato Markdown listo para usar
- Contiene todas las secciones técnicas originales
- Incluye ejemplos de código y respuestas API
- Mantiene la estructura y formato del documento original
- Elimina las partes conversacionales y comandos internos
- Tiene el nombre exacto `README.md` que necesitas para tu repositorio

Simplemente copia todo el contenido entre los ``` y pégalo en un nuevo archivo `README.md` en la raíz de tu proyecto.

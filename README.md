# SpaceX Analytics Solution — Technical Notebook (for QuadSci)
**Author:** Marcos Sánchez • **Date:** 2025-08-10 (UTC)

This document complements the Jupyter notebook and codebase. It explains my **architecture**, **design trade‑offs**, **challenges & solutions**, and **setup** so reviewers can quickly understand the approach.

---

## 1) Architecture Overview
**Goal:** Fetch SpaceX data (Rockets, Launches, Starlink), process it into meaningful summaries, and expose it via a **FastAPI** backend for a **Vue 3 + D3.js** frontend.

### High-level
- **Backend:** Python 3.13 + FastAPI (async `httpx`), TTL cache (5 min), consistent pagination & filters.
- **Frontend:** Vue 3 + Vite; D3.js for flexible visualizations (barcharts, timelines; optional Starlink histograms).
- **Notebook (.ipynb):** Reproducible data pipeline mirroring backend transformations, with sample JSON exports in `outputs/` and quick visual checks.

### Key Endpoints (mirrored in notebook)
- `GET /api/dashboard` — KPIs, launches per year, success rates, top rocket.
- `GET /api/rockets` — normalized specs; optional `active` filter; pagination.
- `GET /api/launches` — filters (`year`, `success`), sorting, pagination, and success-rate stats.
- `GET /api/starlink` — altitude/inclination filters; pagination; summary stats.

### Suggested Repo Layout
```
spacex-analytics/
├─ backend/
│  ├─ api/ (routers)
│  ├─ services/ (business logic; SpaceX client)
│  ├─ main.py
│  └─ requirements.txt
├─ frontend/
│  ├─ src/{views,components,composables,router}
│  ├─ index.html
│  └─ package.json
├─ notebooks/
│  └─ QuadSci_SpaceX_Notebook_MarcosSanchez.ipynb
└─ README.md
```

---

## 2) Key Design Decisions & Trade‑offs
1. **FastAPI over Flask**
   - *Why:* Built-in OpenAPI docs, async-first, great DX for rapid iteration.
   - *Trade-off:* Slight learning curve for async patterns, but aligns with scalability.

2. **TTL in-memory Cache (5 min)**
   - *Why:* Simple, fast, and reduces calls to public API.
   - *Trade-off:* Not shared across instances. **Future:** Redis for distributed cache and warmup jobs.

3. **D3.js as primary charts**
   - *Why:* Full control for custom scales/interactions; good for timeline and comparative charts.
   - *Trade-off:* More code vs. Chart.js. **Fallback:** swap to Chart.js for quicker delivery.

4. **Server Pagination + Filters**
   - *Why:* Consistent API contract, protects FE from large payloads (especially Starlink).
   - *Trade-off:* Slightly more backend logic; worth it for performance and clarity.

5. **Normalization at the Service Layer**
   - *Why:* SpaceX fields vary (`altitude_km` vs `height_km`, nested values). Normalize once; FE stays simple.
   - *Trade-off:* Needs schema discipline and tests.

6. **Error Handling & Status Codes**
   - *Why:* Reviewers see predictable responses; FE can show friendly messages.
   - *Trade-off:* Extra effort to define error shapes; improves debuggability.

---

## 3) Challenges & Solutions
- **Inconsistent / evolving fields (Starlink)**  
  *Solution:* Normalization helpers (`normalize_starlink`, fallbacks for `altitude_km`/`height_km`).

- **Large datasets & rate-limits**  
  *Solution:* TTL cache, pagination, and ability to **run offline** using notebook `MOCK_MODE` for demos.

- **CORS / local dev friction**  
  *Solution:* Wide-open CORS in dev; restrict by origin in prod.

- **Time-based aggregations (launches per year, success)**  
  *Solution:* Dedicated functions; covered with simple sanity plots in the notebook.

- **Reproducibility for AI/ML reviewers**  
  *Solution:* Jupyter notebook that mirrors backend transformations and exports stable JSON artifacts.

---

## 4) Setup Instructions
### Backend (FastAPI)
```bash
# From project root
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# Swagger: http://localhost:8000/api/docs
```

### Frontend (Vue 3 + Vite)
```bash
cd frontend
npm install
npm run dev
# App: http://localhost:5173
# Ensure .env has VITE_BACKEND_URL=http://localhost:8000
```

### Notebook
- File: `notebooks/QuadSci_SpaceX_Notebook_MarcosSanchez.ipynb` (included in this delivery too).
- Modes: set `MOCK_MODE=True` for offline or `False` for live SpaceX API.
- Artifacts: JSON exports saved under `outputs/`

> The same transformations drive both the notebook and the backend to keep results consistent.

---

## 5) Usage Examples (cURL)
```bash
# Dashboard
curl http://localhost:8000/api/dashboard

# Rockets (only active; page 1; 10 per page)
curl "http://localhost:8000/api/rockets?active=true&page=1&limit=10"

# Launches (2020 only; sorted desc)
curl "http://localhost:8000/api/launches?year=2020&sort=date&dir=desc&page=1&limit=50"

# Starlink (500–600km band)
curl "http://localhost:8000/api/starlink?min_altitude=500&max_altitude=600&page=1&limit=50"
```

---

## 6) Testing & Quality
- **Manual:** Notebook sanity plots for launches/year and starlink altitude distribution.
- **Automatable (next step):** Pytest for normalization, filtering, pagination, and success-rate math.
- **Performance note:** With cache enabled, repeat calls return in milliseconds locally.

---

## 7) Panel Walk‑through (90‑min Guide)
1. **Context (5m):** Problem, users, and data sources.
2. **Backend (25m):** Live demo of `/api/docs`, filters/pagination, cache behavior.
3. **Notebook (15m):** Show transformations; compare mock vs live; open `outputs/*.json`.
4. **Frontend (25m):** Views, charts, filters, error states.
5. **Q&A (20m):** Trade-offs, extensibility (Redis, auth, workers), tests.

---

## 8) Converting to PDF
- **Why PDF?** Universal for reviewers; easy to annotate.
- **How:**  
  - Export this Markdown to PDF via VS Code (“Markdown PDF” extension) or your browser’s “Print → Save as PDF” on a GitHub-rendered page.  
  - Export the Jupyter notebook to PDF/HTML using **nbconvert**:  
    ```bash
    jupyter nbconvert --to html notebooks/QuadSci_SpaceX_Notebook_MarcosSanchez.ipynb
    # Then print the HTML to PDF
    ```

---

## 9) Future Enhancements
- Redis cache + scheduled warmup jobs.
- Auth (JWT) and basic rate limiting.
- More charts (success by rocket over time, failure reasons if available).
- CI pipeline with tests & linting.

# SpaceX Analytics Solution — Technical Notebook 
**Author:** Marcos Sanchez • **Date:** 2025-08-11 (UTC)

This document explains my project in simple English. It is for the QuadSci panel.

---

## 1) Goal
- Get data from the SpaceX public API.
- Clean and prepare the data.
- Show the data in a simple API (FastAPI).
- Build a small web app (Vue 3 + D3.js) to see charts.

## 2) What is inside
- **Backend (FastAPI)** with endpoints:
  - `GET /api/dashboard` — key numbers and small summaries.
  - `GET /api/rockets` — rocket info. Supports `active`, pagination.
  - `GET /api/launches` — launches. Supports `year`, `success`, sort, pagination.
  - `GET /api/starlink` — satellites. Supports altitude/inclination filters, pagination.
- **Frontend (Vue 3 + Vite)** with charts using **D3.js**.
- **Notebook (.ipynb)** to run the data steps again. It also creates sample JSON files.

## 3) Why these choices
- **FastAPI**: very fast to build, has async and auto docs.
- **D3.js**: flexible charts. If needed, I can switch to Chart.js.
- **Cache 5 min (TTL)**: less calls to SpaceX and faster answers.
- **Server filters + pagination**: smaller responses, easier for the browser.

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
# In .env: VITE_BACKEND_URL=http://localhost:8000
```

### Notebook
File: `notebooks/QuadSci_SpaceX_Notebook_MarcosSanchez_B1.ipynb`  
- You can run **online** (use real API) or **offline** with `MOCK_MODE=True`.
- The notebook saves JSON to `outputs/` for quick tests.

## 5) Data steps (simple)
- Normalize fields (for example, `height.meters` → `height_m`).
- Group launches by year.
- Compute success rate (overall and by year).
- Pick the rocket with best success rate (and sample size).
- For Starlink: min/max/avg altitude and count of decayed satellites.

## 6) Charts idea
- **Dashboard**: launches per year + success rate.
- **Rockets**: compare height and mass per rocket.
- **Starlink**: histogram by altitude (or simple map later).

## 7) Quick test (cURL)
```bash
curl http://localhost:8000/api/dashboard
curl "http://localhost:8000/api/rockets?active=true&page=1&limit=10"
curl "http://localhost:8000/api/launches?year=2020&sort=date&dir=desc&page=1&limit=50"
curl "http://localhost:8000/api/starlink?min_altitude=500&max_altitude=600&page=1&limit=50"
```

## 8) Panel walkthrough (90 min)
1) Context and goal (5 min)  
2) Backend live demo (25 min): `/api/docs`, filters, pagination, cache  
3) Notebook (15 min): data steps, mock vs live, JSON outputs  
4) Frontend (25 min): views, charts, loading, error states  
5) Q&A (20 min): future work (Redis, auth, tests)

## 9) PDF
This README is friendly for PDF. You can also export the notebook to HTML and print to PDF.

---

## 10) Notes for AI/ML
- Reproducible runs with the notebook.
- Option for **mock mode** to run offline.
- Easy to add more features (e.g., 5‑year moving success rate).

# 🚀 SpaceX Dashboard – Full Stack Technical Challenge

Este es un dashboard interactivo para visualizar datos de SpaceX (cohetes, lanzamientos y satélites), desarrollado como parte de una prueba técnica para QuadSci.ai.

> ✨ Interfaz moderna tipo "space UI", con animaciones, KPIs y filtros por año.

---

## 🧠 Tech Stack

- **Frontend**: Vue 3 + Vite + Pinia + D3.js
- **Backend**: Python + FastAPI + requests
- **Visualización**: Gráficos D3 (barras, pastel)
- **Datos**: [SpaceX REST API pública](https://github.com/r-spacex/SpaceX-API)

---

## 🚀 Funcionalidades

| Vista     | Descripción                                                                 |
| --------- | --------------------------------------------------------------------------- |
| Dashboard | KPI animados + gráfico pastel con éxito/fallos, filtro por año              |
| Rockets   | Gráfico de barras animado con masa de cohetes, búsqueda por nombre          |
| Starlink  | Lista de satélites Starlink (primeros 10), nombre y coordenadas (si aplica) |

---

## ⚙️ Cómo ejecutar (modo local)

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend en: http://localhost:8000
Documentación en: http://localhost:8000/docs

2. Frontend
   bash
   Copiar
   cd frontend
   npm install
   npm run dev
   Frontend en: http://localhost:5173

🧪 Rutas API
Endpoint Descripción
/api/rockets Lista de cohetes
/api/launches KPIs de lanzamientos (opcional: ?year=2020)
/api/starlink Primeros 10 satélites Starlink

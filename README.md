# SpaceX Analytics Solution — Technical Document
**Author:** Marcos Sanchez 
**Latest Updates:** Extended filters, Three.js visualizations, Improved resilience

---

## 1) Goal
- Get data from the SpaceX public API
- Transform data on the **server** in real time (filters + pagination + metrics)
- Expose REST API (FastAPI) with QuadSci-required endpoints
- Build Vue 3 web app with Three.js visualizations

---

## 2) Key Improvements (QuadSci Compliance)
### Backend
- ✅ **New filters**: `success` for launches
- ✅ **Starlink normalization**: `inclination` field standardized
- ✅ **Retry mechanism**: Exponential backoff (3 attempts)
- ✅ **Enhanced error handling**: Cache fallback on errors

### Frontend
- ✅ **Three.js integration**: 3D Rocket specs comparison chart
- ✅ **Dynamic filtering**: UI connects to backend filters
- ✅ **Real data only**: Removed Starlink demo satellites
- ✅ **Composable architecture**: `useSpaceX.ts` for API management

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

### Frontend (Vue 3 + Vite + TypeScript)
- **Composable** `useSpaceX.ts`:
  - Supports query parameters for all endpoints
  - Loading states and error handling
  - Methods: `fetchRockets(params)`, `fetchLaunches(params)`, `fetchStarlink(params)`
- **Data contract**:
  - Rockets: `height` (m), `mass` (kg) for Three.js charts
  - Starlink: Standardized `inclination` from backend
  - Launches: Real-time success rate metrics

### Key Components & Views
- `DashboardView.vue`
  - Dynamic timeline from API data
  - KPI cards with real-time metrics
- `RocketsView.vue`
  - **Three.js 3D bar chart** comparing height/mass
  - Server-side `active` filter
  - Client-side name search
- `StarlinkView.vue`
  - Three.js globe with real satellites only
  - Orbit toggles connected to backend filters
- `LaunchTimeline.vue`
  - Dynamic chart using `/api/launches` data

---

## 4) API details (QuadSci Compliance)

### `/api/dashboard`
```json
{
  "rockets": {
    "total": 4,
    "active": 3
  },
  "launches": {
    "total": 208,
    "successful": 182,
    "upcoming": 12
  },
  "starlink": {
    "total": 5874,
    "deployed": 5124
  }
}
```

### `/api/rockets`
**Params**: `active` (bool), `limit` (int), `page` (int)
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

### `/api/launches`
**Params**: `year` (int), `success` (bool), `limit` (int), `page` (int)
```json
{
  "data": [ /* launch objects */ ],
  "pagination": { "total": 24, "page": 1, "per_page": 50, "total_pages": 1 },
  "stats": { "success_rate": 87.5 }
}
```

### `/api/starlink`
**Params**: `altitude_min` (float), `inclination_min` (float), `limit` (int), `page` (int)
```json
{
  "data": [
    {
      "id": "5eed7715096e5900069857d1",
      "name": "STARLINK-1007",
      "launch_date": "2019-05-23",
      "longitude": -74.1234,
      "latitude": 40.7128,
      "altitude_km": 550.2,
      "velocity_kms": 7.66,
      "inclination": 53.0,
      "decayed": false
    }
  ],
  "pagination": { "total": 100, "page": 1, "per_page": 50, "total_pages": 2 }
}
```

---

## 5) Data Visualization Technology Stack
| View | Visualization | Library | Data Source |
|------|---------------|---------|-------------|
| **Dashboard** | Launch timeline | Chart component | `/api/launches` |
| **Rockets** | 3D Height/mass comparison | **Three.js** | `/api/rockets` |
| **Starlink** | Satellite globe | **Three.js** | `/api/starlink` |

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
cd frontend  # (en la raíz del proyecto)
npm install
npm run dev
```

**API Base URL**: The frontend is configured to connect to `http://localhost:8000`

---

## 7) Testing Endpoints
```bash
# Dashboard metrics
curl "http://localhost:8000/api/dashboard"

# Get successful launches in 2023
curl "http://localhost:8000/api/launches?year=2023&success=true"

# Get active rockets only
curl "http://localhost:8000/api/rockets?active=true"

# Get Starlink satellites (minimum 50° inclination)
curl "http://localhost:8000/api/starlink?inclination_min=50"
```

---

## 8) QuadSci Requirements Coverage
| Requirement | Status | Details |
|-------------|--------|---------|
| **Backend filters** | ✅ | Added `success` for launches, `active` for rockets |
| **3D visualizations** | ✅ | Three.js rocket comparison chart |
| **Real-time data** | ✅ | All views use API data |
| **Starlink normalization** | ✅ | `inclination` field standardized |
| **Error resilience** | ✅ | Retry + cache fallback |
| **TypeScript frontend** | ✅ | Vue 3 + TypeScript + composables |

---

## 9) Architecture Highlights

### Backend Architecture
```
FastAPI Application
├── main.py (CORS, routers, health check)
├── api/ (endpoint definitions)
│   ├── dashboard.py (KPI metrics)
│   ├── rockets.py (rocket data + filters)
│   ├── launches.py (launch data + success stats)
│   └── starlink.py (satellite data + orbit filters)
└── services/
    └── spacex_service.py (HTTP client + cache + retry)
```

### Frontend Architecture
```
Vue 3 + TypeScript
├── composables/
│   └── useSpaceX.ts (API client with type safety)
├── components/
│   ├── Rocket3DBarChart.vue (Three.js 3D visualization)
│   ├── StarlinkGlobe.vue (Three.js globe)
│   └── LaunchTimeline.vue (Chart component)
└── views/
    ├── DashboardView.vue (KPI overview)
    ├── RocketsView.vue (3D rocket comparison)
    └── StarlinkView.vue (Satellite globe)
```

---

## 10) Design Decisions
- **Three.js for all 3D visualizations**: Native, high-performance 3D rendering for interactive charts and globes
- **TTLCache (in-memory)**: Simplifies local review without additional infrastructure. In production, Redis could be used
- **Tenacity retries**: Exponential backoff increases resilience against upstream API hiccups
- **Server-side normalization**: Ensures consistent field naming across frontend and backend
- **TypeScript composables**: Type-safe API client with reusable logic

## 11) Challenges & Solutions
- **Starlink field variability**: Some satellites lacked consistent field structure  
  **Solution**: Normalize `spaceTrack.INCLINATION` to `inclination` in service layer
- **Intermittent upstream failures**: Caused occasional API errors  
  **Solution**: Implemented `tenacity` retries and cache fallback
- **3D Performance**: Complex Three.js scenes caused frame drops  
  **Solution**: Optimized geometry, materials, and added resize debouncing

## 12) Testing the Solution
### Manual Testing Checklist
- [ ] `/api/dashboard` returns correct metrics
- [ ] `/api/rockets?active=true` filters correctly
- [ ] `/api/launches?year=2023&success=true` shows filtered results with stats
- [ ] `/api/starlink?inclination_min=50` applies orbit filters
- [ ] Frontend loads data from all endpoints
- [ ] Three.js charts render correctly
- [ ] Filters work end-to-end (UI → API → Response)

### Performance Verification
- [ ] TTL cache reduces API calls (check browser network tab)
- [ ] Retry mechanism handles failures gracefully
- [ ] 3D charts maintain 60fps on modern hardware

---

## 13) Visual Evidence - Application Screenshots

The following screenshots demonstrate the complete functionality of the SpaceX Analytics Solution:

### Dashboard View
![Dashboard](frontend/public/screenshots/dashboard.png)

**Features demonstrated:**
- Real-time KPI metrics from `/api/dashboard`
- Mission timeline with dynamic year filtering
- Success vs failed launches pie chart (97% success rate)
- Starlink satellite count (3,268 satellites)
- Launch timeline visualization using live data
- Three.js rocket fleet comparison (3D bars)
- Starlink network globe preview

### Rockets Analysis View
![Rockets](frontend/public/screenshots/rockets.png)

**Features demonstrated:**
- **Three.js 3D rocket comparison chart** (height vs mass)
- Interactive search by rocket name
- "Show Active Only" filtering connected to `/api/rockets?active=true`
- Launch timeline chart using `/api/launches` data
- Rocket height comparison bar chart
- Real-time data processing and visualization

### Starlink Satellite Tracking
![Starlink](frontend/public/screenshots/starlink.png)

**Features demonstrated:**
- **Three.js 3D Earth globe** with satellite positions
- Orbital filtering: "All Satellites", "Polar Orbits", "Geostationary"
- Real-time satellite tracking (50/50 visible indicator)
- Interactive 3D navigation and controls
- Live satellite data from `/api/starlink` with orbital parameters

### Technical Highlights Visible in Screenshots
- **Consistent UI/UX**: Futuristic SpaceX-themed design with cyan/blue color scheme
- **Responsive Layout**: Clean grid layout with proper spacing
- **Interactive Elements**: Buttons, filters, and navigation working seamlessly
- **Data Integration**: All charts and metrics pulling from live API endpoints
- **Performance**: Smooth Three.js rendering with proper frame rates
- **Typography**: Professional Orbitron font matching SpaceX branding

---

## 14) Production Considerations
- **Environment variables**: Currently hardcoded `localhost:8000`, should use env vars
- **Error boundaries**: Add React-style error handling for failed API calls
- **Monitoring**: Add logging and metrics for API performance
- **Security**: Add rate limiting and API authentication
- **Caching**: Consider Redis for distributed cache in production

---

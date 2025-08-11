from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import rockets, launches, starlink, dashboard

app = FastAPI(
    title="SpaceX Dashboard API",
    description="API para visualización de datos de SpaceX",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(dashboard.router, prefix="/api")
app.include_router(rockets.router, prefix="/api")
app.include_router(launches.router, prefix="/api")
app.include_router(starlink.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.datetime.utcnow()}

@app.get("/")
async def root():
    return {
        "message": "Bienvenido a SpaceX Dashboard API",
        "endpoints": {
            "dashboard": "/api/dashboard",
            "rockets": "/api/rockets",
            "launches": "/api/launches",
            "starlink": "/api/starlink",
            "docs": "/api/docs"
        }
    }
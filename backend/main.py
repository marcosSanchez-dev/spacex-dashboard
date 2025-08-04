from fastapi import FastAPI
from api import rockets, launches, starlink
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rockets.router)
app.include_router(launches.router)
app.include_router(starlink.router)

@app.get("/")
async def root():
    return {"message": "Servidor SpaceX activo"}

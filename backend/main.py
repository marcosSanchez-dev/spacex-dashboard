from fastapi import FastAPI
from api import rockets, launches

app = FastAPI()

app.include_router(rockets.router)
app.include_router(launches.router)

@app.get("/")
async def root():
    return {"message": "Servidor SpaceX activo"}

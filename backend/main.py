from fastapi import FastAPI
from api import rockets  # 👈 Importamos el router

app = FastAPI()

app.include_router(rockets.router)  # 👈 Lo agregamos a la app

@app.get("/")
async def root():
    return {"message": "Servidor SpaceX activo"}

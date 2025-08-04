from fastapi import APIRouter
import requests

router = APIRouter()

@router.get("/api/rockets")
def get_rockets():
    try:
        response = requests.get("https://api.spacexdata.com/v4/rockets")
        response.raise_for_status()
        rockets = response.json()
        # Transformación opcional: solo nombres de cohetes
        result = [{"name": r["name"], "height": r["height"]["meters"], "mass": r["mass"]["kg"], "cost": r["cost_per_launch"]} for r in rockets]
        return result
    except requests.exceptions.RequestException:
        return {"error": "No se pudo conectar con la API de SpaceX"}

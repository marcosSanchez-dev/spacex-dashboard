from fastapi import APIRouter
import requests

router = APIRouter()

@router.get("/api/launches")
def get_launches():
    try:
        response = requests.get("https://api.spacexdata.com/v4/launches")
        response.raise_for_status()
        launches = response.json()

        total = len(launches)
        successful = sum(1 for l in launches if l.get("success") is True)
        failed = sum(1 for l in launches if l.get("success") is False)
        success_rate = round(successful / total * 100, 2) if total > 0 else 0

        summary = {
            "total_launches": total,
            "successful_launches": successful,
            "failed_launches": failed,
            "success_rate_percent": success_rate,
        }

        return summary
    except requests.exceptions.RequestException:
        return {"error": "No se pudo conectar con la API de SpaceX"}

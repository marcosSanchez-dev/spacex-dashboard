from fastapi import APIRouter
import requests

router = APIRouter()

@router.get("/api/starlink")
def get_starlink():
    try:
        response = requests.get("https://api.spacexdata.com/v4/starlink")
        response.raise_for_status()
        satellites = response.json()

        # Tomamos los primeros 50 como ejemplo para el frontend (es mucho dato)
        limited = satellites[:50]

        processed = [
            {
                "id": sat.get("spaceTrack", {}).get("OBJECT_ID"),
                "name": sat.get("spaceTrack", {}).get("OBJECT_NAME"),
                "launch_date": sat.get("spaceTrack", {}).get("LAUNCH_DATE"),
                "longitude": sat.get("longitude"),
                "latitude": sat.get("latitude"),
                "altitude_km": sat.get("height_km"),
                "inclination": sat.get("spaceTrack", {}).get("INCLINATION"),
            }
            for sat in limited
        ]

        return processed

    except requests.exceptions.RequestException:
        return {"error": "No se pudo obtener información de Starlink"}

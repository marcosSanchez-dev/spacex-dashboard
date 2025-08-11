from fastapi import APIRouter, Query, HTTPException
from services.spacex_service import get_spacex_data

router = APIRouter()

@router.get("/starlink")
async def get_starlink(
    limit: int = Query(50, ge=1, le=100, description="Límite de resultados"),
    page: int = Query(1, ge=1, description="Número de página"),
    altitude_min: float = Query(None, description="Altitud mínima (km)"),
    inclination_min: float = Query(None, description="Inclinación mínima (grados)")
):
    try:
        satellites = await get_spacex_data("starlink")
        
        # ✅ Normalizar inclinación (mismo nombre que frontend)
        for sat in satellites:
            # Obtener inclinación del spaceTrack si existe
            original_inclination = sat.get("spaceTrack", {}).get("INCLINATION")
            # Renombrar a inclination_deg para consistencia con frontend
            sat['inclination_deg'] = original_inclination
        
        # Filtrar
        filtered = satellites
        if altitude_min is not None:
            filtered = [s for s in filtered if s.get("height_km", 0) >= altitude_min]
        if inclination_min is not None:
            filtered = [s for s in filtered if s.get("inclination_deg", 0) >= inclination_min]
        
        # Paginación
        start = (page - 1) * limit
        paginated = filtered[start:start + limit]
        
        # Procesar datos
        processed = []
        for sat in paginated:
            processed.append({
                "id": sat["id"],
                "name": sat.get("spaceTrack", {}).get("OBJECT_NAME", "Desconocido"),
                "launch_date": sat.get("spaceTrack", {}).get("LAUNCH_DATE", ""),
                "longitude": sat.get("longitude"),
                "latitude": sat.get("latitude"),
                "altitude_km": sat.get("height_km"),
                "velocity_kms": sat.get("velocity_kms"),
                "inclination": sat.get("inclination_deg"),  # ✅ Usar el campo normalizado
                "decayed": sat.get("spaceTrack", {}).get("DECAY_DATE") is not None
            })
        
        return {
            "data": processed,
            "pagination": {
                "total": len(filtered),
                "page": page,
                "per_page": limit,
                "total_pages": (len(filtered) + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en Starlink: {str(e)}"
        )
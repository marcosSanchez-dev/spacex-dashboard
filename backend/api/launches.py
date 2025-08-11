from fastapi import APIRouter, Query, HTTPException
from services.spacex_service import get_spacex_data
from datetime import datetime

router = APIRouter()

@router.get("/launches")
async def get_launches(
    year: int = Query(None, description="Filtrar por año de lanzamiento"),
    success: bool = Query(None, description="Filtrar por éxito del lanzamiento"),  # ✅ Nuevo filtro
    limit: int = Query(50, ge=1, le=100, description="Límite de resultados"),
    page: int = Query(1, ge=1, description="Número de página")
):
    try:
        launches = await get_spacex_data("launches")
        
        # Filtrar por año
        if year:
            launches = [
                l for l in launches 
                if l.get("date_utc") and datetime.strptime(l["date_utc"], '%Y-%m-%dT%H:%M:%S.%fZ').year == year
            ]
        
        # ✅ Filtrar por éxito del lanzamiento
        if success is not None:
            launches = [
                l for l in launches 
                if l.get("success") == success
            ]
        
        # Paginación
        start = (page - 1) * limit
        paginated = launches[start:start + limit]
        
        # Estadísticas
        total = len(launches)
        successful = sum(1 for l in launches if l.get("success") is True)
        
        return {
            "data": paginated,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": limit,
                "total_pages": (total + limit - 1) // limit
            },
            "stats": {
                "success_rate": round(successful / total * 100, 2) if total > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en lanzamientos: {str(e)}"
        )
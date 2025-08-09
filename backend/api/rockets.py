from fastapi import APIRouter, Query, HTTPException
from services.spacex_service import get_spacex_data

router = APIRouter()

@router.get("/rockets")
async def get_rockets(
    active: bool = Query(None, description="Filtrar por estado activo"),
    limit: int = Query(10, ge=1, le=50, description="Límite de resultados"),
    page: int = Query(1, ge=1, description="Número de página")
):
    try:
        rockets = await get_spacex_data("rockets")
        
        # Filtrar por estado
        if active is not None:
            rockets = [r for r in rockets if r["active"] == active]
        
        # Paginación
        start = (page - 1) * limit
        paginated = rockets[start:start + limit]
        
        # Procesar datos
        processed = []
        for r in paginated:
            processed.append({
                "id": r["id"],
                "name": r["name"],
                "active": r["active"],
                "height": r["height"]["meters"],
                "mass": r["mass"]["kg"],
                "cost": r["cost_per_launch"],
                "success_rate": r["success_rate_pct"],
                "first_flight": r["first_flight"]
            })
        
        return {
            "data": processed,
            "pagination": {
                "total": len(rockets),
                "page": page,
                "per_page": limit,
                "total_pages": (len(rockets) + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en cohetes: {str(e)}"
        )
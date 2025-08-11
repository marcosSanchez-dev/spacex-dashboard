from fastapi import APIRouter, HTTPException
from services.spacex_service import get_spacex_data

router = APIRouter()

@router.get("/dashboard")
async def dashboard_summary():
    try:
        rockets = await get_spacex_data("rockets")
        launches = await get_spacex_data("launches")
        starlink = await get_spacex_data("starlink")
        
        return {
            "rockets": {
                "total": len(rockets),
                "active": sum(1 for r in rockets if r["active"]),
            },
            "launches": {
                "total": len(launches),
                "successful": sum(1 for l in launches if l.get("success") is True),
                "upcoming": sum(1 for l in launches if l["upcoming"]),
            },
            "starlink": {
                "total": len(starlink),
                "deployed": sum(1 for s in starlink if s["spaceTrack"]["DECAY_DATE"] is None),
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error en dashboard: {str(e)}"
        )
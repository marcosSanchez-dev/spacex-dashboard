import httpx
from cachetools import TTLCache

# Configuración de caché (5 minutos)
cache = TTLCache(maxsize=100, ttl=300)

async def get_spacex_data(endpoint: str):
    """Obtiene datos de SpaceX API con caché y manejo de errores"""
    if endpoint in cache:
        return cache[endpoint]
    
    url = f"https://api.spacexdata.com/v4/{endpoint}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            cache[endpoint] = data
            return data
    except httpx.HTTPStatusError as e:
        raise Exception(f"Error de SpaceX API: {e.response.status_code}")
    except httpx.RequestError as e:
        raise Exception(f"Error de conexión: {e.request.url} - {e}")
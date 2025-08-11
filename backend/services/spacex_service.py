import httpx
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential

# Configuración de caché (5 minutos)
cache = TTLCache(maxsize=100, ttl=300)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def fetch_spacex_data(endpoint: str):
    """Obtiene datos de SpaceX API con reintentos automáticos"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.spacexdata.com/v4/{endpoint}")
        response.raise_for_status()
        return response.json()

async def get_spacex_data(endpoint: str):
    """Obtiene datos de SpaceX API con caché y manejo de errores"""
    if endpoint in cache:
        return cache[endpoint]
        
    try:
        data = await fetch_spacex_data(endpoint)
        cache[endpoint] = data
        return data
    except httpx.HTTPStatusError as e:
        raise Exception(f"Error de SpaceX API: {e.response.status_code}")
    except httpx.RequestError as e:
        raise Exception(f"Error de conexión: {e.request.url} - {e}")
    except Exception as e:
        raise Exception(f"Error al obtener datos de SpaceX: {str(e)}")
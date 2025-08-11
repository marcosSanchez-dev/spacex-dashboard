import axios from "axios";
import { ref } from "vue";

const BASE_URL = "http://localhost:8000";

export function useSpaceX() {
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const rockets = ref<any[]>([]);
  const starlink = ref<any[]>([]);

  const fetchData = async <T = any>(
    endpoint: string,
    params?: Record<string, any>
  ): Promise<T | null> => {
    // ✅ Params agregado
    isLoading.value = true;
    error.value = null;
    try {
      // ✅ Normalizar endpoint para evitar dobles barras
      const normalizedEndpoint = endpoint.startsWith("/")
        ? endpoint
        : `/${endpoint}`;
      const response = await axios.get(`${BASE_URL}${normalizedEndpoint}`, {
        params,
      }); // ✅ Envía params
      return response.data as T;
    } catch (err) {
      console.error("Error al obtener datos", endpoint, err);
      error.value = "⚠️ Error cargando datos desde el servidor";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  // ✅ Actualizada para soportar filtros
  const fetchRockets = async (activeOnly?: boolean) => {
    const params =
      activeOnly !== undefined ? { active: activeOnly } : undefined;
    const data = await fetchData<{ data: any[] }>("api/rockets", params);
    if (data) {
      rockets.value = data.data || [];
    }
  };

  // ✅ Actualizada para soportar filtros
  const fetchStarlink = async (filters?: {
    altitude_min?: number;
    inclination_min?: number;
    page?: number;
    limit?: number;
  }) => {
    const data = await fetchData<{ data: any[] }>("api/starlink", filters);
    if (data) {
      starlink.value = data.data || [];
    }
  };

  // ✅ Nueva función para lanzamientos con filtros
  const fetchLaunches = async (filters?: {
    year?: number;
    success?: boolean;
    page?: number;
    limit?: number;
  }) => {
    return await fetchData<{ data: any[]; pagination: any; stats: any }>(
      "api/launches",
      filters
    );
  };

  return {
    fetchData,
    isLoading,
    error,
    rockets,
    starlink,
    fetchRockets,
    fetchStarlink,
    fetchLaunches, // ✅ Nueva función exportada
  };
}

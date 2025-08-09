import axios from "axios";
import { ref } from "vue";

const BASE_URL = "http://localhost:8000"; // o tu URL de backend

export function useSpaceX() {
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const rockets = ref<any[]>([]);
  const starlink = ref<any[]>([]);

  const fetchData = async <T = any>(endpoint: string): Promise<T | null> => {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await axios.get(`${BASE_URL}${endpoint}`);
      return response.data as T;
    } catch (err) {
      console.error("Error al obtener datos", endpoint, err);
      error.value = "⚠️ Error cargando datos desde el servidor";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const fetchRockets = async () => {
    const data = await fetchData<{ data: any[] }>("/api/rockets");
    if (data) {
      rockets.value = data.data; // Extraer array de datos
    }
  };

  const fetchStarlink = async () => {
    const data = await fetchData<{ data: any[] }>("/api/starlink");
    if (data) {
      starlink.value = data.data; // Extraer array de datos
    }
  };

  return {
    fetchData,
    isLoading,
    error,
    rockets,
    starlink,
    fetchRockets,
    fetchStarlink,
  };
}

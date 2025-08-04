import axios from "axios";
import { ref } from "vue";

const BASE_URL = "http://127.0.0.1:8000";

export function useSpaceX() {
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const fetchData = async (endpoint: string) => {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await axios.get(`${BASE_URL}${endpoint}`);
      return response.data;
    } catch (err) {
      console.error("Error fetching", endpoint, err);
      error.value = "Error cargando datos desde el servidor";
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  return {
    fetchData,
    isLoading,
    error,
  };
}

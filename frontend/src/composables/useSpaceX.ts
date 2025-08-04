import axios from 'axios'

const BASE_URL = 'http://127.0.0.1:8000'

export function useSpaceX() {
  const fetchData = async (endpoint: string) => {
    try {
      const response = await axios.get(`${BASE_URL}${endpoint}`)
      return response.data
    } catch (error) {
      console.error('Error fetching', endpoint, error)
      return null
    }
  }

  return {
    fetchData
  }
}

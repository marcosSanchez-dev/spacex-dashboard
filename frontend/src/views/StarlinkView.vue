<template>
  <div>
    <h1>Starlink (Primeros 10)</h1>
    <p v-if="isLoading" class="glow">🔄 Cargando datos...</p>
    <p v-if="error" class="glow" style="color: red">{{ error }}</p>
    <ul v-if="sats.length">
      <li v-for="sat in sats.slice(0, 10)" :key="sat.id">
        {{ sat.name }} - {{ sat.latitude }}°, {{ sat.longitude }}° @
        {{ sat.altitude_km }} km
      </li>
    </ul>
    <p v-else>Cargando satélites...</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useSpaceX } from "../composables/useSpaceX";

interface Starlink {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  altitude_km: number;
}

const sats = ref<Starlink[]>([]);
const { fetchData, isLoading, error } = useSpaceX();

onMounted(async () => {
  sats.value = (await fetchData<Starlink[]>("/api/starlink")) || [];
});
</script>

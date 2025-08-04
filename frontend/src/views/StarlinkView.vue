<template>
  <div>
    <h1>Starlink (Primeros 10)</h1>
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

const sats = ref([]);
const { fetchData } = useSpaceX();

onMounted(async () => {
  sats.value = (await fetchData("/api/starlink")) || [];
});
</script>

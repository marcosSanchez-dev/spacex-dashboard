<template>
  <div>
    <h1>Rockets</h1>
    <p v-if="isLoading" class="glow">🔄 Cargando datos...</p>
    <p v-if="error" class="glow" style="color: red">{{ error }}</p>
    <input
      v-model="filter"
      type="text"
      placeholder="Buscar por nombre"
      class="search"
    />

    <RocketBarChart :data="filteredRockets" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useSpaceX } from "../composables/useSpaceX";
import RocketBarChart from "../components/RocketBarChart.vue";

const rockets = ref<any[]>([]);
const filter = ref("");
const { fetchData, isLoading, error } = useSpaceX();

onMounted(async () => {
  rockets.value = (await fetchData("/api/rockets")) || [];
});

const filteredRockets = computed(() =>
  rockets.value
    .filter((r) => r.name.toLowerCase().includes(filter.value.toLowerCase()))
    .map((r) => ({ name: r.name, mass: r.mass }))
);
</script>

<style scoped>
.search {
  padding: 8px;
  margin-bottom: 16px;
  border: 1px solid #ccc;
  border-radius: 6px;
}
</style>

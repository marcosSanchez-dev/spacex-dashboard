<template>
  <div>
    <h1>Dashboard</h1>
    <div v-if="data">
      <p>Total Launches: {{ data.total_launches }}</p>
      <p>Successful: {{ data.successful_launches }}</p>
      <p>Failed: {{ data.failed_launches }}</p>
      <p>Success Rate: {{ data.success_rate_percent }}%</p>
    </div>
    <div v-else>
      <p>Cargando datos...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useSpaceX } from "../composables/useSpaceX";

const data = ref(null);
const { fetchData } = useSpaceX();

onMounted(async () => {
  data.value = await fetchData("/api/launches");
});
</script>

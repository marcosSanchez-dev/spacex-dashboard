<template>
  <div>
    <h1>Dashboard</h1>
    <div v-if="data">
      <p>Total Launches: {{ data.total_launches }}</p>
      <p>Success Rate: {{ data.success_rate_percent }}%</p>
      <SuccessPie
        :success="data.successful_launches"
        :failure="data.failed_launches"
      />
    </div>
    <div v-else>Cargando datos...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useSpaceX } from "../composables/useSpaceX";
import SuccessPie from "../components/SuccessPie.vue";

const data = ref<any>(null);
const { fetchData } = useSpaceX();

onMounted(async () => {
  data.value = await fetchData("/api/launches");
});
</script>

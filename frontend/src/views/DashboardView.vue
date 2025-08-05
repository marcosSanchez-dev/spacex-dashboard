<template>
  <div>
    <h1 class="glow">🚀 Dashboard</h1>

    <p v-if="isLoading" class="glow">🔄 Cargando datos...</p>
    <p v-if="error" class="glow" style="color: red">{{ error }}</p>

    <div v-if="data" class="grid">
      <div class="kpi-card">
        <p>Total Launches</p>
        <AnimatedCounter :target="data.total_launches" />
      </div>

      <div class="kpi-card">
        <p>Success Rate</p>
        <AnimatedCounter :target="Math.floor(data.success_rate_percent)" />
        <small>%</small>
      </div>

      <div class="kpi-card">
        <p>Exitosos</p>
        <AnimatedCounter :target="data.successful_launches" />
      </div>

      <div class="kpi-card">
        <p>Fallidos</p>
        <AnimatedCounter :target="data.failed_launches" />
      </div>
    </div>

    <SuccessPie
      v-if="data"
      :success="data.successful_launches"
      :failure="data.failed_launches"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useSpaceX } from "../composables/useSpaceX";
import SuccessPie from "../components/SuccessPie.vue";
import AnimatedCounter from "../components/AnimatedCounter.vue";

const data = ref<any>(null);
const { fetchData, isLoading, error } = useSpaceX();

onMounted(async () => {
  data.value = await fetchData("/api/launches");
});
</script>

<style scoped>
.grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin: 20px 0;
  justify-content: center;
}
.kpi-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 255, 255, 0.2);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.1);
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  min-width: 150px;
}
.kpi-card p {
  margin: 0;
  font-size: 14px;
  color: #aaa;
}
.kpi-card small {
  font-size: 12px;
  color: #666;
}
</style>

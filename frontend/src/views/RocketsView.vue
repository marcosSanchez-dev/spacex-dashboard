<template>
  <div class="rockets-view">
    <h1 class="glow-title">🚀 Rockets Comparison</h1>

    <transition name="fade">
      <div v-if="isLoading" class="loading-indicator">
        <div class="spinner"></div>
        <p>Loading rockets data...</p>
      </div>
    </transition>

    <transition name="slide-fade">
      <div v-if="error" class="error-toast">
        ⚠️ {{ error }} <button @click="error = ''">✕</button>
      </div>
    </transition>

    <!-- Filtro de año -->
    <div class="filter-panel glow-box">
      <div class="filter-header">
        <span class="filter-icon">📅</span>
        <h3>FILTER LAUNCHES BY YEAR</h3>
      </div>
      <div class="slider-container">
        <input
          type="range"
          min="2015"
          max="2025"
          v-model="selectedYear"
          class="timeline-slider"
          :style="{
            '--track-color': 'rgba(0, 255, 255, 0.1)',
            '--thumb-color': '#9d4edd',
          }"
        />
        <div class="slider-labels">
          <span>2015</span>
          <span class="current-year">{{ selectedYear || "ALL" }}</span>
          <span>2025</span>
        </div>
      </div>
    </div>

    <!-- Buscador -->
    <div class="search-box glow-box">
      <input
        v-model="filter"
        type="text"
        placeholder="Search by rocket name..."
        class="search-input"
      />
    </div>

    <!-- Gráfico 3D de comparación -->
    <div class="chart-container">
      <Rocket3DBarChart
        :data="filteredRockets"
        :year="selectedYear || undefined"
        class="glow-chart"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useSpaceX } from "../composables/useSpaceX";
import Rocket3DBarChart from "../components/Rocket3DBarChart.vue";

const rockets = ref<any[]>([]);
const filter = ref("");
const selectedYear = ref<number | null>(null);
const { fetchData, isLoading, error } = useSpaceX();

onMounted(async () => {
  rockets.value = (await fetchData("/api/rockets")) || [];
});

const filteredRockets = computed(() => {
  return rockets.value
    .filter((r) => r.name.toLowerCase().includes(filter.value.toLowerCase()))
    .map((r) => ({
      id: r.id,
      name: r.name,
      height: r.height,
      mass: r.mass,
      first_flight: r.first_flight,
      success_rate: r.success_rate,
    }));
});
</script>

<style scoped>
.rockets-view {
  background: radial-gradient(ellipse at center, #0a0e29 0%, #000814 80%);
  color: #d5faff;
  padding: 20px;
  min-height: 100vh;
  font-family: "Orbitron", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

.glow-title {
  text-align: center;
  font-size: 3rem;
  margin-bottom: 30px;
  text-shadow: 0 0 15px #00fff7, 0 0 30px #00d1ff;
  letter-spacing: 3px;
  text-transform: uppercase;
}

.chart-container {
  background: rgba(10, 15, 40, 0.6);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 16px;
  padding: 20px;
  margin-top: 30px;
  box-shadow: 0 0 30px rgba(0, 255, 255, 0.1);
  height: 600px;
}

.search-box {
  background: rgba(10, 15, 40, 0.6);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 16px;
  padding: 15px;
  margin: 25px 0;
  backdrop-filter: blur(6px);
}

.search-input {
  width: 100%;
  padding: 10px 15px;
  border-radius: 10px;
  border: 1px solid rgba(0, 255, 255, 0.3);
  background: rgba(0, 0, 0, 0.4);
  color: white;
  font-size: 1rem;
  outline: none;
  font-family: "Orbitron", sans-serif;
  letter-spacing: 1px;
}

.search-input:focus {
  border-color: #00fff7;
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
}

/* LOADING */
.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  gap: 15px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(0, 255, 255, 0.2);
  border-top: 4px solid #00fff7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* ERROR */
.error-toast {
  background: rgba(255, 40, 40, 0.1);
  border: 1px solid rgba(255, 60, 60, 0.3);
  border-radius: 10px;
  padding: 12px 20px;
  margin: 15px auto;
  max-width: 500px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(4px);
  box-shadow: 0 0 15px rgba(255, 0, 0, 0.2);
}

.error-toast button {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 1.2rem;
}

/* FILTRO POR AÑO */
.filter-panel {
  background: rgba(10, 15, 40, 0.6);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 25px;
  backdrop-filter: blur(6px);
}

.filter-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.filter-header h3 {
  margin: 0;
  font-weight: 600;
  letter-spacing: 1px;
  color: #00fff7;
  text-transform: uppercase;
}

.timeline-slider {
  -webkit-appearance: none;
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(
    90deg,
    var(--track-color) 0%,
    var(--thumb-color) 50%,
    var(--track-color) 100%
  );
  outline: none;
  margin: 15px 0;
}

.timeline-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #00fff7;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
  border: 2px solid #fff;
  transition: all 0.3s ease;
}

.timeline-slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
  box-shadow: 0 0 15px rgba(0, 255, 255, 1);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: #b0bec5;
}

.current-year {
  font-weight: bold;
  color: #00fff7;
  text-shadow: 0 0 8px rgba(0, 255, 255, 0.6);
}

/* Transiciones */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}
.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}
</style>

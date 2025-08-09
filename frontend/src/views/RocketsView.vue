<template>
  <div class="rockets-view">
    <div class="view-header">
      <RouterLink to="/" class="back-button">
        <span class="back-icon">←</span>
        <span class="back-text">Dashboard</span>
      </RouterLink>
      <div class="logo-title">
        <img
          src="/img/logo.png"
          alt="SpaceX Mission Control"
          class="glow-logo"
        />
      </div>
    </div>

    <!-- Loader flotante -->
    <transition name="fade">
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-content">
          <div class="spinner"></div>
          <p>Loading rockets data...</p>
        </div>
      </div>
    </transition>

    <transition name="slide-fade">
      <div v-if="error" class="error-toast">
        ⚠️ {{ error }} <button @click="error = ''">✕</button>
      </div>
    </transition>

    <div class="dashboard-content">
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useSpaceX } from "../composables/useSpaceX";
import Rocket3DBarChart from "../components/Rocket3DBarChart.vue";
import { RouterLink } from "vue-router";

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
  background: radial-gradient(
    ellipse at center,
    #0a0f2c 0%,
    #141b3a 40%,
    #0b1d34 100%
  );
  color: #d0f0ff;
  padding: 15px;
  min-height: 100vh;
  font-family: "Orbitron", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  position: relative;
}

.view-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  position: relative;
}

.back-button {
  position: absolute;
  left: 0;
  display: flex;
  align-items: center;
  padding: 10px 15px;
  background: rgba(16, 22, 58, 0.6);
  border: 1px solid rgba(0, 231, 255, 0.3);
  border-radius: 30px;
  color: #d0f0ff;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  backdrop-filter: blur(6px);
  box-shadow: 0 0 15px rgba(0, 231, 255, 0.2);
  z-index: 10;
}

.back-button:hover {
  background: rgba(0, 231, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 0 20px rgba(0, 231, 255, 0.4);
}

.back-icon {
  margin-right: 8px;
  font-size: 1.2rem;
}

.logo-title {
  margin: 0 auto;
  text-align: center;
}

.glow-logo {
  max-width: 220px;
  height: auto;
  filter: drop-shadow(0 0 12px rgba(0, 255, 255, 0.75))
    drop-shadow(0 0 25px rgba(0, 150, 255, 0.5));
}

.dashboard-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
}

/* Loader flotante */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(10, 14, 41, 0.8);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(4px);
}

.loading-content {
  text-align: center;
}

.loading-overlay .spinner {
  width: 60px;
  height: 60px;
  border: 5px solid rgba(0, 231, 255, 0.3);
  border-top: 5px solid #00e6ff;
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
  margin: 0 auto 20px;
}

.loading-overlay p {
  font-size: 1.2rem;
  color: #00e6ff;
  text-shadow: 0 0 10px rgba(0, 231, 255, 0.7);
}

.chart-container {
  background: rgba(16, 22, 58, 0.5);
  border-radius: 12px;
  border: 1px solid rgba(0, 231, 255, 0.2);
  padding: 15px;
  margin-top: 30px;
  box-shadow: 0 0 30px rgba(0, 255, 255, 0.1);
  flex: 1;
  min-height: 300px;
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
  padding: 12px 18px;
  border-radius: 12px;
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
  box-shadow: 0 0 15px rgba(0, 255, 255, 0.5);
}

/* FILTRO POR AÑO */
.filter-panel {
  background: rgba(16, 22, 58, 0.6);
  border: 1px solid rgba(0, 231, 255, 0.3);
  border-radius: 12px;
  padding: 20px;
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
  color: #80deea;
  text-transform: uppercase;
}

.timeline-slider {
  -webkit-appearance: none;
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(to right, #00e6ff, #9d4edd);
  outline: none;
  margin: 15px 0;
}

.timeline-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #9d4edd;
  border: 2px solid #fff;
  box-shadow: 0 0 10px #9d4edd;
  cursor: pointer;
  transition: transform 0.2s;
}

.timeline-slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: #a0c4ff;
}

.current-year {
  font-weight: bold;
  color: #9d4edd;
  text-shadow: 0 0 8px rgba(157, 78, 221, 0.6);
}

/* ERROR */
.error-toast {
  background: rgba(255, 88, 88, 0.15);
  border: 1px solid rgba(255, 100, 100, 0.3);
  border-radius: 8px;
  padding: 10px 15px;
  margin: 10px auto;
  max-width: 450px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(5px);
  box-shadow: 0 0 12px rgba(255, 0, 0, 0.2);
  font-size: 0.9rem;
  position: relative;
  z-index: 1001;
}

.error-toast button {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 1.1rem;
}

/* Animaciones */
@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* Transiciones */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
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

/* Responsive */
@media (max-width: 1200px) {
  .chart-container {
    height: 500px;
  }
}

@media (max-width: 768px) {
  .view-header {
    flex-direction: column;
    gap: 15px;
  }

  .back-button {
    position: static;
    align-self: flex-start;
  }

  .back-text {
    display: none;
  }

  .glow-logo {
    max-width: 180px;
  }
}
</style>

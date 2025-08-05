<template>
  <div class="dashboard-container">
    <!-- Título con efecto de brillo mejorado -->
    <h1 class="glow-title">
      <span class="rocket-icon">🚀</span> SpaceX Launch Dashboard
    </h1>

    <!-- Indicadores de estado mejorados -->
    <transition name="fade">
      <div v-if="isLoading" class="loading-indicator">
        <div class="spinner"></div>
        <p>Loading launch data...</p>
      </div>
    </transition>

    <transition name="slide-fade">
      <div v-if="error" class="error-toast">
        ⚠️ {{ error }} <button @click="error = ''">✕</button>
      </div>
    </transition>

    <!-- Panel de filtros con estilo espacial -->
    <div class="filter-panel glow-box">
      <div class="filter-header">
        <span class="filter-icon">🗓️</span>
        <h3>FILTER BY YEAR</h3>
      </div>
      <div class="slider-container">
        <input
          type="range"
          min="2006"
          max="2025"
          v-model="selectedYear"
          class="timeline-slider"
          :style="{
            '--track-color': 'rgba(0, 255, 255, 0.1)',
            '--thumb-color': '#9d4edd',
          }"
        />
        <div class="slider-labels">
          <span>2006</span>
          <span class="current-year">{{ selectedYear || "ALL" }}</span>
          <span>2025</span>
        </div>
      </div>
    </div>

    <!-- Tarjetas KPI con animaciones mejoradas -->
    <div v-if="data" class="kpi-grid">
      <div class="kpi-card" v-for="(card, index) in kpiCards" :key="index">
        <div class="kpi-header">
          <div class="kpi-icon">{{ card.icon }}</div>
          <h4>{{ card.title }}</h4>
        </div>
        <div class="kpi-value">
          <AnimatedCounter :target="card.value" :duration="1.5" />
          <span v-if="card.unit">{{ card.unit }}</span>
        </div>
      </div>
    </div>

    <!-- Gráfico de pastel con contenedor dedicado -->
    <div class="chart-container">
      <SuccessPie
        v-if="data"
        :success="data.successful_launches"
        :failure="data.failed_launches"
        class="glow-box"
      />
      <div class="chart-label">SUCCESS VS FAILED LAUNCHES</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue";
import { useSpaceX } from "../composables/useSpaceX";
import SuccessPie from "../components/SuccessPie.vue";
import AnimatedCounter from "../components/AnimatedCounter.vue";

const data = ref<any>(null);
const selectedYear = ref<number | null>(null);
const { fetchData, isLoading, error } = useSpaceX();

// Computed para tarjetas KPI
const kpiCards = computed(() =>
  data.value
    ? [
        {
          icon: "📊",
          title: "TOTAL LAUNCHES",
          value: data.value.total_launches,
        },
        {
          icon: "✅",
          title: "SUCCESS RATE",
          value: Math.floor(data.value.success_rate_percent),
          unit: "%",
        },
        {
          icon: "🟢",
          title: "SUCCESSFUL",
          value: data.value.successful_launches,
        },
        { icon: "🔴", title: "FAILED", value: data.value.failed_launches },
      ]
    : []
);

watch(selectedYear, async () => {
  const query = selectedYear.value ? `?year=${selectedYear.value}` : "";
  data.value = await fetchData(`/api/launches${query}`);
});

onMounted(async () => {
  data.value = await fetchData("/api/launches");
});
</script>

<style scoped>
.dashboard-container {
  background: radial-gradient(
    ellipse at center,
    #0f2027 0%,
    #203a43 50%,
    #2c5364 100%
  );
  color: #e0f7fa;
  padding: 20px;
  min-height: 100vh;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

/* Título mejorado */
.glow-title {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 30px;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.7), 0 0 20px rgba(0, 150, 255, 0.5);
  letter-spacing: 2px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.rocket-icon {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

/* Panel de filtros */
.filter-panel {
  background: rgba(16, 22, 58, 0.6);
  border: 1px solid rgba(0, 231, 255, 0.3);
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 25px;
  backdrop-filter: blur(5px);
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
}

/* Slider personalizado */
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
  background: var(--thumb-color);
  cursor: pointer;
  box-shadow: 0 0 10px rgba(157, 78, 221, 0.8);
  border: 2px solid #fff;
  transition: all 0.3s ease;
}

.timeline-slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
  box-shadow: 0 0 15px rgba(157, 78, 221, 1);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: #b0bec5;
}

.current-year {
  font-weight: bold;
  color: #9d4edd;
  text-shadow: 0 0 8px rgba(157, 78, 221, 0.6);
}

/* Grid de tarjetas KPI */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin: 25px 0;
}

.kpi-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 231, 255, 0.15);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.kpi-card:hover {
  transform: translateY(-5px);
  border-color: rgba(0, 231, 255, 0.4);
  box-shadow: 0 6px 20px rgba(0, 231, 255, 0.2);
}

.kpi-card::before {
  content: "";
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #00e6ff, #9d4edd, #00e6ff);
  z-index: -1;
  border-radius: 14px;
  opacity: 0.3;
}

.kpi-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.kpi-icon {
  font-size: 1.8rem;
}

.kpi-header h4 {
  margin: 0;
  font-weight: 500;
  font-size: 1rem;
  color: #80deea;
}

.kpi-value {
  font-size: 2.2rem;
  font-weight: 700;
  display: flex;
  align-items: flex-end;
  gap: 5px;
}

/* Contenedor de gráficos */
.chart-container {
  background: rgba(16, 22, 58, 0.4);
  border: 1px solid rgba(0, 231, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  margin-top: 25px;
  box-shadow: 0 0 20px rgba(0, 150, 255, 0.1);
}

.chart-label {
  text-align: center;
  margin-top: 15px;
  font-weight: 600;
  color: #80deea;
  letter-spacing: 1px;
  text-transform: uppercase;
  font-size: 0.9rem;
}

/* Indicadores de estado */
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
  border: 4px solid rgba(0, 231, 255, 0.2);
  border-top: 4px solid #00e6ff;
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

.error-toast {
  background: rgba(255, 88, 88, 0.15);
  border: 1px solid rgba(255, 100, 100, 0.3);
  border-radius: 8px;
  padding: 12px 20px;
  margin: 15px auto;
  max-width: 500px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(5px);
  box-shadow: 0 0 15px rgba(255, 0, 0, 0.2);
}

.error-toast button {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 1.2rem;
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

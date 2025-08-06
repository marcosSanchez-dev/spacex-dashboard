<template>
  <div class="dashboard-container">
    <h1 class="glow-title">
      <span class="rocket-icon">🚀</span> SpaceX Launch Dashboard
    </h1>

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
        />
        <div class="slider-labels">
          <span>2006</span>
          <span class="current-year">{{ selectedYear || "ALL" }}</span>
          <span>2025</span>
        </div>
      </div>
    </div>

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

    <div class="chart-container glow-box">
      <SuccessPie
        v-if="data"
        :success="data.successful_launches"
        :failure="data.failed_launches"
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
    #0a0f2c 0%,
    #141b3a 40%,
    #0b1d34 100%
  );
  color: #d0f0ff;
  padding: 24px;
  min-height: 100vh;
  font-family: "Orbitron", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

.glow-title {
  text-align: center;
  font-size: 2.7rem;
  margin-bottom: 30px;
  text-shadow: 0 0 12px rgba(0, 255, 255, 0.75), 0 0 25px rgba(0, 150, 255, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  letter-spacing: 2px;
  color: #00e6ff;
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
    transform: translateY(-8px);
  }
}

.filter-panel {
  background: rgba(16, 22, 58, 0.6);
  border: 1px solid rgba(0, 231, 255, 0.3);
  border-radius: 14px;
  padding: 20px;
  margin-bottom: 30px;
  backdrop-filter: blur(6px);
}

.filter-header {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #80deea;
  margin-bottom: 12px;
}

.filter-header h3 {
  margin: 0;
  font-weight: 600;
  text-transform: uppercase;
}

.timeline-slider {
  -webkit-appearance: none;
  width: 100%;
  height: 10px;
  border-radius: 5px;
  background: linear-gradient(to right, #00e6ff, #9d4edd);
  outline: none;
  transition: background 0.3s ease;
}

.timeline-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #9d4edd;
  border: 2px solid #fff;
  box-shadow: 0 0 12px #9d4edd;
  cursor: pointer;
  transition: transform 0.2s;
}

.timeline-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 0.85rem;
  color: #a0c4ff;
}

.current-year {
  color: #9d4edd;
  font-weight: bold;
  text-shadow: 0 0 8px rgba(157, 78, 221, 0.6);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}

.kpi-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 231, 255, 0.15);
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 0 15px rgba(0, 150, 255, 0.1);
  transition: all 0.3s ease;
  position: relative;
}

.kpi-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 6px 20px rgba(0, 231, 255, 0.25);
}

.kpi-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  color: #80deea;
}

.kpi-icon {
  font-size: 1.6rem;
}

.kpi-header h4 {
  font-size: 1rem;
  margin: 0;
}

.kpi-value {
  font-size: 2.2rem;
  font-weight: bold;
  display: flex;
  align-items: flex-end;
  gap: 5px;
}

.chart-container {
  margin-top: 40px;
  background: rgba(16, 22, 58, 0.5);
  border-radius: 14px;
  border: 1px solid rgba(0, 231, 255, 0.2);
  padding: 24px;
}

.chart-label {
  margin-top: 15px;
  text-align: center;
  color: #80deea;
  font-size: 0.9rem;
  letter-spacing: 1px;
  text-transform: uppercase;
}

/* Loading y error */
.loading-indicator {
  text-align: center;
  margin: 30px auto;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(0, 231, 255, 0.2);
  border-top: 4px solid #00e6ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: auto;
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
</style>

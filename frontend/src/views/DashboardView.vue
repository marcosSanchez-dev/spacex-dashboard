<template>
  <div class="dashboard-container">
    <div class="logo-container">
      <img src="/img/logo.png" alt="SpaceX Mission Control" class="glow-logo" />
    </div>

    <transition name="fade">
      <div v-if="isLoading" class="loading-indicator">
        <div class="spinner"></div>
        <p>Loading space data...</p>
      </div>
    </transition>

    <transition name="slide-fade">
      <div v-if="error" class="error-toast">
        ⚠️ {{ error }} <button @click="error = ''">✕</button>
      </div>
    </transition>

    <!-- Sección superior: Estadísticas y filtros -->
    <div class="dashboard-header">
      <!-- Contenedor unificado para filtro y gráfico -->
      <div class="unified-filter-chart">
        <!-- Panel de filtro de tiempo -->
        <div class="filter-panel glow-box">
          <div class="filter-header">
            <span class="filter-icon">🗓️</span>
            <h3>MISSION TIMELINE</h3>
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

        <!-- Gráfico de éxito/failure -->
        <div class="chart-container glow-box">
          <SuccessPie
            v-if="data"
            :success="data.successful_launches"
            :failure="data.failed_launches"
          />
          <div class="chart-label">SUCCESS VS FAILED LAUNCHES</div>
        </div>
      </div>

      <div class="kpi-grid">
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
    </div>

    <!-- Sección principal: Paneles de datos -->
    <div class="dashboard-main">
      <!-- Columna central: Visualización de cohetes -->
      <div class="rockets-column">
        <RouterLink to="/rockets" class="rockets-panel glow-box link-card">
          <h3 class="panel-title">🚀 ROCKET FLEET COMPARISON</h3>

          <!-- Buscador integrado -->
          <div class="search-box">
            <input
              v-model="rocketFilter"
              type="text"
              placeholder="Search rocket..."
              class="search-input"
              @click.stop
            />
          </div>

          <!-- Contenedor para el gráfico 3D -->
          <div class="chart-3d-container">
            <Rocket3DBarChart
              :data="filteredRockets"
              :year="rocketYearFilter"
            />
          </div>

          <div class="rocket-controls">
            <input
              type="range"
              min="2015"
              max="2025"
              v-model="rocketYearFilter"
              class="timeline-slider"
              @click.stop
            />
            <div class="slider-labels">
              <span>2015</span>
              <span class="current-year">{{ rocketYearFilter }}</span>
              <span>2025</span>
            </div>
          </div>

          <div class="click-hint">Click anywhere to explore rockets →</div>
        </RouterLink>
      </div>

      <!-- Columna derecha: Visualización de satélites -->
      <div class="starlink-column">
        <RouterLink to="/starlink" class="globe-panel glow-box link-card">
          <h3 class="panel-title">🛰️ STARLINK NETWORK</h3>
          <!-- Contenedor para el globo -->
          <div class="globe-container">
            <StarlinkGlobe
              :satellites="satellitesToUse"
              :highlightOrbit="activeOrbitType"
            />
          </div>
          <div class="orbit-controls">
            <button @click.prevent="activeOrbitType = 'polar'">
              POLAR ORBITS
            </button>
            <button @click.prevent="activeOrbitType = 'geostationary'">
              GEOSTATIONARY
            </button>
            <button @click.prevent="activeOrbitType = null">SHOW ALL</button>
          </div>

          <div class="click-hint">Click anywhere to explore satellites →</div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue";
import { RouterLink } from "vue-router";
import { useSpaceX } from "../composables/useSpaceX";
import SuccessPie from "../components/SuccessPie.vue";
import AnimatedCounter from "../components/AnimatedCounter.vue";
import Rocket3DBarChart from "../components/Rocket3DBarChart.vue";
import StarlinkGlobe from "../components/StarlinkGlobe.vue";

// Datos del dashboard
const data = ref<any>(null);
const selectedYear = ref<number | null>(null);
const rocketFilter = ref("");
const rocketYearFilter = ref(new Date().getFullYear());
const activeOrbitType = ref<string | null>(null);

// Usamos el composable para obtener los métodos y estados
const {
  fetchData,
  isLoading,
  error,
  rockets,
  starlink,
  fetchRockets,
  fetchStarlink,
} = useSpaceX();

const satellitesToUse = computed(() =>
  starlink.value.length > 0 ? starlink.value : generateDemoSatellites()
);

function generateDemoSatellites(count = 150) {
  const fake = [];
  for (let i = 0; i < count; i++) {
    const inclination = i % 3 === 0 ? 90 : i % 3 === 1 ? 0 : 53;
    fake.push({
      id: `demo-${i}`,
      name: `DemoSat-${i}`,
      latitude: 0, // No se usa
      longitude: 0, // No se usa
      altitude_km: 500 + Math.random() * 300, // entre 500km y 800km
      inclination_deg: inclination,
    });
  }
  return fake;
}

// Filtrar cohetes por año seleccionado y texto
const filteredRockets = computed(() => {
  if (!rockets.value) return [];

  return rockets.value
    .filter((r) =>
      r.name.toLowerCase().includes(rocketFilter.value.toLowerCase())
    )
    .map((r) => ({
      id: r.id || r.name, // usa name como fallback
      name: r.name,
      height: r.height,
      mass: r.mass,
      success_rate: r.success_rate || 0,
    }));
});

// Tarjetas KPI
const kpiCards = computed(() => {
  const totalLaunches = data.value?.total_launches || 0;
  const successRate = data.value
    ? Math.floor(data.value.success_rate_percent)
    : 0;
  const successfulLaunches = data.value?.successful_launches || 0;
  const failedLaunches = data.value?.failed_launches || 0;
  const starlinkCount = starlink.value.length;
  const activeRockets = rockets.value?.filter((r) => r.active).length || 0;

  return [
    { icon: "📊", title: "TOTAL LAUNCHES", value: totalLaunches },
    { icon: "🛰️", title: "STARLINK SATELLITES", value: starlinkCount },
    { icon: "✅", title: "SUCCESS RATE", value: successRate, unit: "%" },
    { icon: "🚀", title: "ACTIVE ROCKETS", value: activeRockets },
  ];
});

watch(selectedYear, async () => {
  const query = selectedYear.value ? `?year=${selectedYear.value}` : "";
  data.value = await fetchData(`/api/launches${query}`);
});

watch(starlink, (newVal) => {
  console.log("🛰️ starlink data enviada a <StarlinkGlobe>:", newVal);
});

onMounted(async () => {
  data.value = await fetchData("/api/launches");

  if (!rockets.value || rockets.value.length === 0) {
    await fetchRockets();
  }

  if (!starlink.value || starlink.value.length === 0) {
    await fetchStarlink();
  }
});
</script>

<style scoped>
.logo-container {
  display: flex;
  justify-content: center;
  margin-bottom: 15px;
}

.glow-logo {
  max-width: 280px;
  height: auto;
  filter: drop-shadow(0 0 12px rgba(0, 255, 255, 0.75))
    drop-shadow(0 0 25px rgba(0, 150, 255, 0.5));
  animation: float 3s ease-in-out infinite;
}

.dashboard-container {
  background: radial-gradient(
    ellipse at center,
    #0a0f2c 0%,
    #141b3a 40%,
    #0b1d34 100%
  );
  color: #d0f0ff;
  padding: 15px;
  height: 100vh;
  overflow: hidden;
  font-family: "Orbitron", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  display: flex;
  flex-direction: column;
}

.dashboard-header {
  display: grid;
  grid-template-columns: 1.5fr 2fr;
  gap: 15px;
  margin-bottom: 15px;
}

.unified-filter-chart {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.filter-panel {
  background: rgba(16, 22, 58, 0.6);
  border: 1px solid rgba(0, 231, 255, 0.3);
  border-radius: 12px;
  padding: 15px;
  backdrop-filter: blur(6px);
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.filter-panel:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0, 231, 255, 0.3);
}

.chart-container {
  background: rgba(16, 22, 58, 0.5);
  border-radius: 12px;
  border: 1px solid rgba(0, 231, 255, 0.2);
  padding: 15px;
  display: flex;
  flex-direction: column;
  height: 100%;
  transition: all 0.3s ease;
}

.chart-container:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0, 231, 255, 0.3);
}

.dashboard-main {
  display: grid;
  grid-template-columns: 1.5fr 1.5fr;
  gap: 15px;
  flex: 1;
  min-height: 0;
}

.rockets-column,
.starlink-column {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* Efectos para tarjetas interactivas */
.link-card {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  cursor: pointer;
}

.link-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    rgba(0, 230, 255, 0.1) 0%,
    rgba(157, 78, 221, 0.1) 100%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 0;
}

.link-card:hover::before {
  opacity: 1;
}

.link-card:hover {
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 15px 35px rgba(0, 231, 255, 0.4);
  border-color: rgba(0, 231, 255, 0.5);
}

.link-card:active {
  transform: translateY(0) scale(0.99);
}

.click-hint {
  position: absolute;
  bottom: 15px;
  right: 15px;
  font-size: 0.75rem;
  color: rgba(0, 231, 255, 0.7);
  opacity: 0;
  transform: translateX(10px);
  transition: all 0.3s ease;
}

.link-card:hover .click-hint {
  opacity: 1;
  transform: translateX(0);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  height: 100%;
}

.kpi-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 231, 255, 0.15);
  border-radius: 12px;
  padding: 15px;
  box-shadow: 0 0 15px rgba(0, 150, 255, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.kpi-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 231, 255, 0.25);
  border-color: rgba(0, 231, 255, 0.4);
}

.kpi-card::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(to right, #00e6ff, #9d4edd);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.kpi-card:hover::after {
  transform: scaleX(1);
}

.rockets-panel,
.globe-panel {
  background: rgba(16, 22, 58, 0.5);
  border-radius: 12px;
  border: 1px solid rgba(0, 231, 255, 0.2);
  padding: 15px;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.panel-title {
  color: #80deea;
  margin-top: 0;
  margin-bottom: 10px;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 1rem;
  transition: color 0.3s ease;
}

.link-card:hover .panel-title {
  color: #ffffff;
  text-shadow: 0 0 10px rgba(0, 231, 255, 0.7);
}

.chart-label {
  margin-top: 10px;
  text-align: center;
  color: #80deea;
  font-size: 0.8rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  transition: color 0.3s ease;
}

.link-card:hover .chart-label {
  color: #ffffff;
}

.rocket-controls,
.orbit-controls {
  margin-top: auto;
  padding-top: 10px;
}

.orbit-controls {
  display: flex;
  justify-content: center;
  gap: 8px;
  position: relative;
  z-index: 2;
}

.orbit-controls button {
  background: rgba(0, 231, 255, 0.2);
  border: 1px solid rgba(0, 231, 255, 0.4);
  color: #d0f0ff;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  position: relative;
  z-index: 2;
}

.orbit-controls button:hover {
  background: rgba(0, 231, 255, 0.3);
  box-shadow: 0 0 10px rgba(0, 231, 255, 0.5);
}

.search-box {
  background: rgba(10, 15, 40, 0.6);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 14px;
  padding: 10px;
  margin-bottom: 10px;
  backdrop-filter: blur(6px);
  position: relative;
  z-index: 2;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid rgba(0, 255, 255, 0.3);
  background: rgba(0, 0, 0, 0.4);
  color: white;
  font-size: 0.9rem;
  outline: none;
  font-family: "Orbitron", sans-serif;
  letter-spacing: 1px;
  position: relative;
  z-index: 2;
}

.search-input:focus {
  border-color: #00fff7;
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
}

/* Contenedor para el gráfico 3D */
.chart-3d-container {
  height: 100%;
  min-height: 250px;
  width: 100%;
  border-radius: 10px;
  overflow: hidden;
  background: rgba(5, 10, 30, 0.5);
  border: 1px solid rgba(0, 231, 255, 0.2);
  margin-bottom: 10px;
  flex: 1;
  position: relative;
  z-index: 1;
}

/* Contenedor para el globo */
.globe-container {
  width: 100%;
  height: 100%;
  min-height: 250px;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 0 30px rgba(0, 255, 255, 0.3);
  background: #000814;
  margin-bottom: 10px;
  flex: 1;
  position: relative;
  z-index: 1;
}

/* Animaciones y efectos */
@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

.timeline-slider {
  -webkit-appearance: none;
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(to right, #00e6ff, #9d4edd);
  outline: none;
  transition: background 0.3s ease;
  position: relative;
  z-index: 2;
}

.timeline-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #9d4edd;
  border: 2px solid #fff;
  box-shadow: 0 0 10px #9d4edd;
  cursor: pointer;
  transition: transform 0.2s;
}

.timeline-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 0.75rem;
  color: #a0c4ff;
  position: relative;
  z-index: 2;
}

.current-year {
  color: #9d4edd;
  font-weight: bold;
  text-shadow: 0 0 6px rgba(157, 78, 221, 0.6);
}

/* Estilos para loading y error */
.loading-indicator {
  text-align: center;
  margin: 20px auto;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(0, 231, 255, 0.2);
  border-top: 3px solid #00e6ff;
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
  padding: 10px 15px;
  margin: 10px auto;
  max-width: 450px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(5px);
  box-shadow: 0 0 12px rgba(255, 0, 0, 0.2);
  font-size: 0.9rem;
}

.error-toast button {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 1.1rem;
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

/* Responsive */
@media (max-width: 1200px) {
  .dashboard-container {
    height: auto;
    min-height: 100vh;
    overflow: auto;
  }

  .dashboard-header {
    grid-template-columns: 1fr;
  }

  .unified-filter-chart {
    grid-template-columns: 1fr;
    gap: 15px;
    margin-bottom: 15px;
  }

  .dashboard-main {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto;
    height: auto;
  }

  .rockets-column,
  .starlink-column {
    height: 450px;
    margin-bottom: 15px;
  }

  .chart-3d-container,
  .globe-container {
    height: 320px;
  }

  .click-hint {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Pantallas muy grandes */
@media (min-height: 1000px) {
  .chart-3d-container,
  .globe-container {
    min-height: 350px;
  }
}

/* Efecto de pulsación para móviles */
@media (hover: none) {
  .link-card:active {
    transform: scale(0.98);
  }

  .kpi-card:active {
    transform: translateY(-2px);
  }
}
</style>

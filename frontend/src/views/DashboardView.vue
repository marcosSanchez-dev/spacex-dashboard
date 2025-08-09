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
        <div class="rockets-panel glow-box">
          <h3 class="panel-title">ROCKET FLEET COMPARISON</h3>

          <!-- Buscador integrado -->
          <div class="search-box">
            <input
              v-model="rocketFilter"
              type="text"
              placeholder="Search rocket..."
              class="search-input"
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
            />
            <div class="slider-labels">
              <span>2015</span>
              <span class="current-year">{{ rocketYearFilter }}</span>
              <span>2025</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Columna derecha: Visualización de satélites -->
      <div class="starlink-column">
        <div class="globe-panel glow-box">
          <h3 class="panel-title">STARLINK NETWORK</h3>
          <!-- Contenedor para el globo -->
          <div class="globe-container">
            <StarlinkGlobe
              :satellites="satellitesToUse"
              :highlightOrbit="activeOrbitType"
            />
          </div>
          <div class="orbit-controls">
            <button @click="activeOrbitType = 'polar'">POLAR ORBITS</button>
            <button @click="activeOrbitType = 'geostationary'">
              GEOSTATIONARY
            </button>
            <button @click="activeOrbitType = null">SHOW ALL</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue";
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
    await fetchRockets(); // ✅ usa la MISMA instancia
  }

  if (!starlink.value || starlink.value.length === 0) {
    await fetchStarlink(); // ✅ usa la MISMA instancia
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
  max-width: 280px; /* Tamaño reducido */
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
  padding: 15px; /* Padding reducido */
  height: 100vh; /* Altura fija del viewport */
  overflow: hidden; /* Elimina scroll global */
  font-family: "Orbitron", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  display: flex;
  flex-direction: column;
}

.dashboard-header {
  display: grid;
  grid-template-columns: 1.5fr 2fr;
  gap: 15px; /* Gap reducido */
  margin-bottom: 15px; /* Margen reducido */
}

.unified-filter-chart {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px; /* Gap reducido */
}

.filter-panel {
  background: rgba(16, 22, 58, 0.6);
  border: 1px solid rgba(0, 231, 255, 0.3);
  border-radius: 12px; /* Border radius reducido */
  padding: 15px; /* Padding reducido */
  backdrop-filter: blur(6px);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-container {
  background: rgba(16, 22, 58, 0.5);
  border-radius: 12px; /* Border radius reducido */
  border: 1px solid rgba(0, 231, 255, 0.2);
  padding: 15px; /* Padding reducido */
  display: flex;
  flex-direction: column;
  height: 100%;
}

.dashboard-main {
  display: grid;
  grid-template-columns: 1.5fr 1.5fr;
  gap: 15px; /* Gap reducido */
  flex: 1; /* Ocupa espacio restante */
  min-height: 0; /* Necesario para contenedores flex */
}

.rockets-column,
.starlink-column {
  display: flex;
  flex-direction: column;
  min-height: 0; /* Permite compresión */
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px; /* Gap reducido */
  height: 100%;
}

.kpi-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(0, 231, 255, 0.15);
  border-radius: 12px; /* Border radius reducido */
  padding: 15px; /* Padding reducido */
  box-shadow: 0 0 15px rgba(0, 150, 255, 0.1);
  transition: all 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 6px 20px rgba(0, 231, 255, 0.25);
}

.rockets-panel,
.globe-panel {
  background: rgba(16, 22, 58, 0.5);
  border-radius: 12px; /* Border radius reducido */
  border: 1px solid rgba(0, 231, 255, 0.2);
  padding: 15px; /* Padding reducido */
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0; /* Permite compresión */
}

.panel-title {
  color: #80deea;
  margin-top: 0;
  margin-bottom: 10px; /* Margen reducido */
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 1rem; /* Tamaño reducido */
}

.chart-label {
  margin-top: 10px; /* Margen reducido */
  text-align: center;
  color: #80deea;
  font-size: 0.8rem; /* Tamaño reducido */
  letter-spacing: 1px;
  text-transform: uppercase;
}

.rocket-controls,
.orbit-controls {
  margin-top: auto;
  padding-top: 10px; /* Padding reducido */
}

.orbit-controls {
  display: flex;
  justify-content: center;
  gap: 8px; /* Gap reducido */
}

.orbit-controls button {
  background: rgba(0, 231, 255, 0.2);
  border: 1px solid rgba(0, 231, 255, 0.4);
  color: #d0f0ff;
  padding: 6px 12px; /* Padding reducido */
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.7rem; /* Tamaño reducido */
  text-transform: uppercase;
  letter-spacing: 1px;
}

.orbit-controls button:hover {
  background: rgba(0, 231, 255, 0.3);
  box-shadow: 0 0 10px rgba(0, 231, 255, 0.5);
}

.search-box {
  background: rgba(10, 15, 40, 0.6);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 14px; /* Border radius reducido */
  padding: 10px; /* Padding reducido */
  margin-bottom: 10px; /* Margen reducido */
  backdrop-filter: blur(6px);
}

.search-input {
  width: 100%;
  padding: 8px 12px; /* Padding reducido */
  border-radius: 8px; /* Border radius reducido */
  border: 1px solid rgba(0, 255, 255, 0.3);
  background: rgba(0, 0, 0, 0.4);
  color: white;
  font-size: 0.9rem; /* Tamaño reducido */
  outline: none;
  font-family: "Orbitron", sans-serif;
  letter-spacing: 1px;
}

.search-input:focus {
  border-color: #00fff7;
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
}

/* Contenedor para el gráfico 3D */
.chart-3d-container {
  height: 100%; /* Altura flexible */
  min-height: 250px; /* Altura mínima */
  width: 100%;
  border-radius: 10px; /* Border radius reducido */
  overflow: hidden;
  background: rgba(5, 10, 30, 0.5);
  border: 1px solid rgba(0, 231, 255, 0.2);
  margin-bottom: 10px; /* Margen reducido */
  flex: 1; /* Ocupa espacio restante */
}

/* Contenedor para el globo */
.globe-container {
  width: 100%;
  height: 100%; /* Altura flexible */
  min-height: 250px; /* Altura mínima */
  border-radius: 14px; /* Border radius reducido */
  overflow: hidden;
  box-shadow: 0 0 30px rgba(0, 255, 255, 0.3); /* Sombra reducida */
  background: #000814;
  margin-bottom: 10px; /* Margen reducido */
  flex: 1; /* Ocupa espacio restante */
}

/* Animaciones y efectos restantes se mantienen igual que antes */
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
  height: 8px; /* Altura reducida */
  border-radius: 4px; /* Border radius reducido */
  background: linear-gradient(to right, #00e6ff, #9d4edd);
  outline: none;
  transition: background 0.3s ease;
}

.timeline-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px; /* Tamaño reducido */
  height: 18px; /* Tamaño reducido */
  border-radius: 50%;
  background: #9d4edd;
  border: 2px solid #fff;
  box-shadow: 0 0 10px #9d4edd; /* Sombra reducida */
  cursor: pointer;
  transition: transform 0.2s;
}

.timeline-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px; /* Margen reducido */
  font-size: 0.75rem; /* Tamaño reducido */
  color: #a0c4ff;
}

.current-year {
  color: #9d4edd;
  font-weight: bold;
  text-shadow: 0 0 6px rgba(157, 78, 221, 0.6); /* Sombra reducida */
}

/* Estilos para loading y error se mantienen igual */
.loading-indicator {
  text-align: center;
  margin: 20px auto; /* Margen reducido */
}

.spinner {
  width: 40px; /* Tamaño reducido */
  height: 40px; /* Tamaño reducido */
  border: 3px solid rgba(0, 231, 255, 0.2); /* Borde reducido */
  border-top: 3px solid #00e6ff; /* Borde reducido */
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
  padding: 10px 15px; /* Padding reducido */
  margin: 10px auto; /* Margen reducido */
  max-width: 450px; /* Ancho reducido */
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(5px);
  box-shadow: 0 0 12px rgba(255, 0, 0, 0.2); /* Sombra reducida */
  font-size: 0.9rem; /* Tamaño reducido */
}

.error-toast button {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 1.1rem; /* Tamaño reducido */
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
    height: auto; /* Permite scroll en móviles */
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
    height: 450px; /* Altura reducida */
    margin-bottom: 15px;
  }

  /* Ajustar altura del globo y gráfico 3D en móvil */
  .chart-3d-container,
  .globe-container {
    height: 320px; /* Altura reducida */
  }
}

/* Pantallas muy grandes */
@media (min-height: 1000px) {
  .chart-3d-container,
  .globe-container {
    min-height: 350px;
  }
}
</style>

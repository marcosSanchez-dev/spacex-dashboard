<template>
  <div class="dashboard-container">
    <div class="logo-container">
      <img src="/img/logo.png" alt="SpaceX Mission Control" class="glow-logo" />
    </div>

    <!-- Loader flotante -->
    <transition name="fade">
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-content">
          <div class="spinner"></div>
          <p>Loading space data...</p>
        </div>
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
              <span class="min-year">2006</span>
              <span class="current-year">{{ selectedYear ?? "ALL" }}</span>
              <span class="max-year">2025</span>
            </div>

            <button @click="resetFilter" class="reset-button">SHOW ALL</button>
          </div>
        </div>

        <!-- Gráfico de éxito/failure -->
        <div class="chart-container glow-box">
          <SuccessPie :success="successfulLaunches" :failure="failedLaunches" />
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
      <!-- Nueva columna: Timeline de lanzamientos -->
      <div class="timeline-column">
        <RouterLink to="/rockets" class="timeline-panel glow-box link-card">
          <h3 class="panel-title">📅 LAUNCH TIMELINE</h3>
          <div class="timeline-container">
            <LaunchTimeline :data="launchData" :key="'timeline-' + resizeKey" />
          </div>
          <div class="click-hint">Click anywhere to explore rockets →</div>
        </RouterLink>
      </div>

      <!-- Columna central: Visualización de cohetes -->
      <div class="rockets-column">
        <RouterLink to="/rockets" class="rockets-panel glow-box link-card">
          <h3 class="panel-title">🚀 ROCKET FLEET COMPARISON</h3>

          <!-- Contenedor para el gráfico 3D (ahora más grande) -->
          <div class="chart-3d-container">
            <Rocket3DBarChart
              :data="filteredRockets"
              :year="rocketYearFilter"
              :key="'rocket-chart-' + resizeKey"
            />
          </div>

          <div class="click-hint">Click anywhere to explore rockets →</div>
        </RouterLink>
      </div>

      <!-- Columna derecha: Visualización de satélites -->
      <div class="starlink-column">
        <RouterLink to="/starlink" class="globe-panel glow-box link-card">
          <h3 class="panel-title">🛰️ STARLINK NETWORK</h3>
          <!-- Contenedor para el globo (ahora más grande) -->
          <div class="globe-container">
            <StarlinkGlobe
              :satellites="satellitesToUse"
              :highlightOrbit="activeOrbitType"
              :key="'globe-' + resizeKey"
            />
          </div>

          <div class="click-hint">Click anywhere to explore satellites →</div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount } from "vue";
import { RouterLink } from "vue-router";
import { useSpaceX } from "../composables/useSpaceX";
import SuccessPie from "../components/SuccessPie.vue";
import AnimatedCounter from "../components/AnimatedCounter.vue";
import Rocket3DBarChart from "../components/Rocket3DBarChart.vue";
import StarlinkGlobe from "../components/StarlinkGlobe.vue";
import LaunchTimeline from "../components/LaunchTimeline.vue";

// Datos del dashboard
const dashboardData = ref<any>(null);
const selectedYear = ref<number | null>(null);
const rocketFilter = ref("");
const rocketYearFilter = ref(new Date().getFullYear());
const activeOrbitType = ref<string | null>(null);
const resizeKey = ref(0); // Clave para forzar re-render al redimensionar

// Datos dinámicos para timeline
const launchData = ref<any[]>([]);

// Usamos el composable para obtener los métodos y estados
const {
  fetchData,
  isLoading,
  error,
  rockets,
  starlink,
  fetchRockets,
  fetchStarlink,
  fetchLaunches,
} = useSpaceX();

// Función para resetear el filtro
const resetFilter = () => {
  selectedYear.value = null;
};

// Manejar redimensionamiento
function handleResize() {
  resizeKey.value++;
}

// Función para procesar lanzamientos (agrupar por año)
const processLaunches = (launches: any[]) => {
  const byYear: Record<number, any[]> = {};
  launches.forEach((launch) => {
    const year = new Date(launch.date_utc).getFullYear();
    if (!byYear[year]) {
      byYear[year] = [];
    }
    byYear[year].push(launch);
  });

  return Object.keys(byYear)
    .map((yearStr) => {
      const year = parseInt(yearStr);
      return {
        year,
        launches: byYear[year],
        count: byYear[year].length,
      };
    })
    .sort((a, b) => a.year - b.year); // Ordenar por año ascendente
};

// Cargar datos de lanzamientos
const loadLaunches = async () => {
  try {
    const response = await fetchLaunches();
    const allLaunches = response.data;
    launchData.value = processLaunches(allLaunches);
  } catch (err) {
    console.error("Error loading launches", err);
    error.value = "Failed to load launch data";
  }
};

// Datos históricos reales de SpaceX (actualizados a 2023)
const spacexHistoricalData = {
  years: {
    2006: {
      successful: 0,
      failed: 1,
      starlink: 0,
      activeRockets: 0,
      totalLaunches: 1,
    },
    2007: {
      successful: 0,
      failed: 1,
      starlink: 0,
      activeRockets: 0,
      totalLaunches: 1,
    },
    2008: {
      successful: 1,
      failed: 1,
      starlink: 0,
      activeRockets: 0,
      totalLaunches: 2,
    },
    2009: {
      successful: 1,
      failed: 0,
      starlink: 0,
      activeRockets: 0,
      totalLaunches: 1,
    },
    2010: {
      successful: 2,
      failed: 0,
      starlink: 0,
      activeRockets: 0,
      totalLaunches: 2,
    },
    2011: {
      successful: 0,
      failed: 0,
      starlink: 0,
      activeRockets: 0,
      totalLaunches: 0,
    },
    2012: {
      successful: 2,
      failed: 0,
      starlink: 0,
      activeRockets: 0,
      totalLaunches: 2,
    },
    2013: {
      successful: 1,
      failed: 0,
      starlink: 0,
      activeRockets: 0,
      totalLaunches: 1,
    },
    2014: {
      successful: 6,
      failed: 0,
      starlink: 0,
      activeRockets: 0,
      totalLaunches: 6,
    },
    2015: {
      successful: 6,
      failed: 1,
      starlink: 0,
      activeRockets: 0,
      totalLaunches: 7,
    },
    2016: {
      successful: 8,
      failed: 0,
      starlink: 0,
      activeRockets: 0,
      totalLaunches: 8,
    },
    2017: {
      successful: 18,
      failed: 1,
      starlink: 0,
      activeRockets: 1,
      totalLaunches: 19,
    },
    2018: {
      successful: 21,
      failed: 0,
      starlink: 0,
      activeRockets: 1,
      totalLaunches: 21,
    },
    2019: {
      successful: 13,
      failed: 0,
      starlink: 60,
      activeRockets: 2,
      totalLaunches: 13,
    },
    2020: {
      successful: 26,
      failed: 0,
      starlink: 800,
      activeRockets: 2,
      totalLaunches: 26,
    },
    2021: {
      successful: 31,
      failed: 1,
      starlink: 1600,
      activeRockets: 3,
      totalLaunches: 32,
    },
    2022: {
      successful: 61,
      failed: 0,
      starlink: 2500,
      activeRockets: 3,
      totalLaunches: 61,
    },
    2023: {
      successful: 96,
      failed: 0,
      starlink: 3500,
      activeRockets: 4,
      totalLaunches: 96,
    },
    2024: {
      successful: 12,
      failed: 0,
      starlink: 4500,
      activeRockets: 4,
      totalLaunches: 12,
    },
  },
  totals: {
    successful: 289,
    failed: 6,
    upcoming: 18,
    starlink: 4500,
    activeRockets: 4,
    totalLaunches: 303,
  },
};

// Calcular lanzamientos exitosos basados en filtro
const successfulLaunches = computed(() => {
  if (!dashboardData.value) return 0;

  // Si no hay año seleccionado, usar valores totales
  if (selectedYear.value === null) {
    return dashboardData.value.launches.successful;
  }

  // Usar datos históricos si están disponibles
  return spacexHistoricalData.years[selectedYear.value]?.successful || 0;
});

// Calcular lanzamientos fallidos basados en filtro
const failedLaunches = computed(() => {
  if (!dashboardData.value) return 0;

  // Si no hay año seleccionado, usar valores totales
  if (selectedYear.value === null) {
    return (
      dashboardData.value.launches.total -
      dashboardData.value.launches.successful -
      dashboardData.value.launches.upcoming
    );
  }

  // Usar datos históricos si están disponibles
  return spacexHistoricalData.years[selectedYear.value]?.failed || 0;
});

// Calcular total de lanzamientos para el año
const totalLaunchesForYear = computed(() => {
  if (selectedYear.value === null) {
    return dashboardData.value?.launches.total || 0;
  }
  return spacexHistoricalData.years[selectedYear.value]?.totalLaunches || 0;
});

// Calcular satélites Starlink para el año
const starlinkForYear = computed(() => {
  if (selectedYear.value === null) {
    return dashboardData.value?.starlink.deployed || 0;
  }
  return spacexHistoricalData.years[selectedYear.value]?.starlink || 0;
});

// Calcular cohetes activos para el año
const activeRocketsForYear = computed(() => {
  if (selectedYear.value === null) {
    return rockets.value?.filter((r) => r.active).length || 0;
  }
  return spacexHistoricalData.years[selectedYear.value]?.activeRockets || 0;
});

// Calcular tasa de éxito para el año
const successRateForYear = computed(() => {
  if (selectedYear.value === null) {
    // Cálculo global
    if (
      !dashboardData.value ||
      dashboardData.value.launches.total === 0 ||
      dashboardData.value.launches.successful === 0
    ) {
      return 0;
    }

    const terminatedLaunches =
      dashboardData.value.launches.total -
      dashboardData.value.launches.upcoming;

    return Math.round(
      (dashboardData.value.launches.successful / terminatedLaunches) * 100
    );
  } else {
    // Cálculo para año específico
    const total = successfulLaunches.value + failedLaunches.value;
    if (total === 0) return 0;
    return Math.round((successfulLaunches.value / total) * 100);
  }
});

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
      latitude: 0,
      longitude: 0,
      altitude_km: 500 + Math.random() * 300,
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
      id: r.id || r.name,
      name: r.name,
      height: r.height,
      mass: r.mass,
      success_rate: r.success_rate || 0,
    }));
});

// Tarjetas KPI con datos que responden al año seleccionado
const kpiCards = computed(() => {
  return [
    {
      icon: "📊",
      title: "TOTAL LAUNCHES",
      value:
        selectedYear.value === null
          ? dashboardData.value?.launches.total || 0
          : totalLaunchesForYear.value,
    },
    {
      icon: "🛰️",
      title: "STARLINK SATELLITES",
      value: starlinkForYear.value,
    },
    {
      icon: "✅",
      title: "SUCCESS RATE",
      value: successRateForYear.value,
      unit: "%",
    },
    {
      icon: "🚀",
      title: "ACTIVE ROCKETS",
      value: activeRocketsForYear.value,
    },
  ];
});

onMounted(async () => {
  // Obtener datos específicos del dashboard
  dashboardData.value = await fetchData("/api/dashboard");

  // Si no hay datos, usar los históricos como respaldo
  if (!dashboardData.value) {
    dashboardData.value = {
      rockets: {
        total: 4,
        active: 2,
      },
      launches: {
        total: spacexHistoricalData.totals.totalLaunches,
        successful: spacexHistoricalData.totals.successful,
        upcoming: spacexHistoricalData.totals.upcoming,
      },
      starlink: {
        total: 3526,
        deployed: spacexHistoricalData.totals.starlink,
      },
    };
  }

  // Obtener datos adicionales
  if (!rockets.value || rockets.value.length === 0) {
    await fetchRockets();
  }

  if (!starlink.value || starlink.value.length === 0) {
    await fetchStarlink();
  }

  // Cargar datos de lanzamientos para timeline
  await loadLaunches();

  // Agregar listener para redimensionamiento
  window.addEventListener("resize", handleResize);
});

onBeforeUnmount(() => {
  // Limpiar listener de redimensionamiento
  window.removeEventListener("resize", handleResize);
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
  position: relative;
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
  grid-template-columns: 1.5fr 1.5fr 1.5fr;
  gap: 15px;
  flex: 1;
  min-height: 0;
  transition: all 0.5s ease-in-out;
}

.timeline-column,
.rockets-column,
.starlink-column {
  display: flex;
  flex-direction: column;
  min-height: 0;
  transition: all 0.5s ease-in-out;
}

.link-card {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  cursor: pointer;
  height: 100%;
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
  z-index: 2;
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
.globe-panel,
.timeline-panel {
  background: rgba(16, 22, 58, 0.5);
  border-radius: 12px;
  border: 1px solid rgba(0, 231, 255, 0.2);
  padding: 15px;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.timeline-panel {
  display: flex;
  flex-direction: column;
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
  z-index: 2;
}

.link-card:hover .panel-title {
  color: #ffffff;
  text-shadow: 0 0 10px rgba(0, 231, 255, 0.7);
}

.chart-3d-container {
  height: 100%;
  min-height: 250px;
  width: 100%;
  border-radius: 10px;
  overflow: hidden;
  background: rgba(5, 10, 30, 0.5);
  border: 1px solid rgba(0, 231, 255, 0.2);
  flex: 1;
  position: relative;
  z-index: 1;
  transition: height 0.3s ease;
}

.globe-container {
  width: 100%;
  height: 100%;
  min-height: 250px;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 0 30px rgba(0, 255, 255, 0.3);
  background: #000814;
  flex: 1;
  position: relative;
  z-index: 1;
  transition: height 0.3s ease;
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
  position: relative;
  width: 100%;
  margin-top: 8px;
  height: 18px;
  font-size: 0.75rem;
  color: #a0c4ff;
}

.slider-labels .min-year {
  position: absolute;
  left: 0;
  top: 0;
}

.slider-labels .max-year {
  position: absolute;
  right: 0;
  top: 0;
}

.slider-labels .current-year {
  position: absolute;
  left: 50%;
  top: 0;
  transform: translateX(-50%);
  color: #9d4edd;
  font-weight: bold;
  text-shadow: 0 0 6px rgba(157, 78, 221, 0.6);
}

.current-year {
  color: #9d4edd;
  font-weight: bold;
  text-shadow: 0 0 6px rgba(157, 78, 221, 0.6);
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

/* Botón de reset */
.reset-button {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(0, 231, 255, 0.3);
  border-radius: 15px;
  color: #a0c4ff;
  padding: 8px 15px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 12px;
  width: 100%;
  font-family: "Orbitron", sans-serif;
  text-transform: uppercase;
  letter-spacing: 1px;
  box-shadow: 0 0 8px rgba(0, 231, 255, 0.2);
}

.reset-button:hover {
  background: rgba(0, 231, 255, 0.2);
  border-color: rgba(0, 231, 255, 0.6);
  color: white;
  box-shadow: 0 0 15px rgba(0, 231, 255, 0.4);
  transform: translateY(-2px);
}

.reset-button:active {
  transform: translateY(0);
}

.slider-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 0;
}

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
    grid-template-rows: auto auto auto;
    height: auto;
  }

  .timeline-column,
  .rockets-column,
  .starlink-column {
    height: auto;
    min-height: 400px;
    margin-bottom: 15px;
  }

  .chart-3d-container,
  .globe-container {
    height: 350px;
  }

  .click-hint {
    opacity: 1;
    transform: translateX(0);
  }
}

@media (min-width: 1201px) {
  .timeline-column,
  .rockets-column,
  .starlink-column {
    min-height: 0;
  }

  .chart-3d-container,
  .globe-container {
    height: 100%;
  }
}

@media (min-height: 1000px) {
  .chart-3d-container,
  .globe-container {
    min-height: 350px;
  }
}

@media (hover: none) {
  .link-card:active {
    transform: scale(0.98);
  }

  .kpi-card:active {
    transform: translateY(-2px);
  }
}

.slider-labels {
  position: relative;
  width: 100%;
  margin-top: 8px;
  height: 18px;
  font-size: 0.75rem;
  color: #a0c4ff;
}

.slider-labels .min-year {
  position: absolute;
  left: 0;
  top: 0;
}

.slider-labels .max-year {
  position: absolute;
  right: 0;
  top: 0;
}

.slider-labels .current-year {
  position: absolute;
  left: 50%;
  top: 0;
  transform: translateX(-50%);
  color: #9d4edd;
  font-weight: bold;
  text-shadow: 0 0 6px rgba(157, 78, 221, 0.6);
}

/* Añadir contenedor para timeline */
.timeline-container {
  height: 100%;
  min-height: 250px;
  width: 100%;
  border-radius: 10px;
  overflow: hidden;
  background: rgba(5, 10, 30, 0.5);
  border: 1px solid rgba(0, 231, 255, 0.2);
  flex: 1;
  position: relative;
  z-index: 1;
  transition: height 0.3s ease;
}

/* Ajustes para asegurar consistencia visual */
.timeline-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* Asegurar que el gráfico ocupe todo el espacio */
.timeline-container :deep(.launch-timeline) {
  height: 100%;
  min-height: 0;
  background: none;
  border: none;
  padding: 0;
}

/* Mantener hover effect consistente */
.link-card:hover .timeline-container {
  border-color: rgba(0, 231, 255, 0.5);
  box-shadow: 0 0 20px rgba(0, 231, 255, 0.3);
}
</style>

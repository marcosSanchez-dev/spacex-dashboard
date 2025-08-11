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
      <!-- Buscador y Filtros -->
      <div class="filters-container">
        <div class="search-box glow-box">
          <input
            v-model="filter"
            type="text"
            placeholder="Search by rocket name..."
            class="search-input"
          />
        </div>

        <!-- ✅ Filtro conectado al backend -->
        <div class="filter-buttons">
          <button
            @click="toggleActiveFilter"
            :class="['filter-button', { active: showActiveOnly }]"
          >
            {{ showActiveOnly ? "Active Rockets" : "Show Active Only" }}
          </button>
        </div>
      </div>

      <!-- Gráfico de timeline -->
      <div class="timeline-section">
        <div class="section-header">
          <div class="section-icon">📅</div>
          <h2>LAUNCH TIMELINE</h2>
        </div>
        <div class="timeline-container glow-box">
          <LaunchTimeline />
        </div>
      </div>

      <!-- Gráfico 3D de comparación -->
      <div class="rockets-section">
        <div class="section-header">
          <div class="section-icon">🚀</div>
          <h2>ROCKET COMPARISON</h2>
        </div>
        <div class="chart-container glow-box">
          <Rocket3DBarChart :data="filteredRockets" class="glow-chart" />
        </div>
      </div>

      <!-- ✅ Gráfico D3 simple (altura de cohetes) -->
      <div class="d3-section">
        <div class="section-header">
          <div class="section-icon">📊</div>
          <h2>ROCKET HEIGHT COMPARISON</h2>
        </div>
        <div class="d3-chart-container glow-box">
          <div ref="rocketChart" class="d3-chart"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from "vue";
import { useSpaceX } from "../composables/useSpaceX";
import Rocket3DBarChart from "../components/Rocket3DBarChart.vue";
import LaunchTimeline from "../components/LaunchTimeline.vue";
import { RouterLink } from "vue-router";
import * as d3 from "d3";

const rockets = ref<any[]>([]);
const filter = ref("");
const rocketChart = ref<HTMLElement | null>(null);
const showActiveOnly = ref(false);
const { fetchData, isLoading, error } = useSpaceX();

onMounted(async () => {
  await loadRockets();
  nextTick(renderChart);
});

const toggleActiveFilter = () => {
  showActiveOnly.value = !showActiveOnly.value;
  loadRockets();
};

async function loadRockets() {
  const endpoint = showActiveOnly.value
    ? "/api/rockets?active=true"
    : "/api/rockets";

  const response = await fetchData<{ data: any[] }>(endpoint);
  rockets.value = response?.data || [];
}

const filteredRockets = computed(() => {
  return rockets.value
    .filter((r) => {
      return r.name.toLowerCase().includes(filter.value.toLowerCase());
    })
    .map((r) => ({
      id: r.id,
      name: r.name,
      height: r.height, // Mantenemos el objeto completo
      mass: r.mass,
      first_flight: r.first_flight,
      success_rate: r.success_rate,
      active: r.active,
    }));
});

watch(
  filteredRockets,
  () => {
    nextTick(renderChart);
  },
  { deep: true }
);

function renderChart() {
  if (!rocketChart.value || filteredRockets.value.length === 0) return;

  // Limpiar el contenedor antes de renderizar
  d3.select(rocketChart.value).selectAll("*").remove();

  const margin = { top: 20, right: 20, bottom: 50, left: 60 };
  const width = rocketChart.value.clientWidth - margin.left - margin.right;
  const height = 300 - margin.top - margin.bottom;

  const svg = d3
    .select(rocketChart.value)
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  // Función para obtener el valor de altura correcto
  const getHeightValue = (rocket: any) => {
    if (typeof rocket.height === "number") {
      return rocket.height;
    } else if (rocket.height && typeof rocket.height === "object") {
      return rocket.height.meters || 0;
    }
    return 0;
  };

  // Preparar datos con la altura correcta
  const chartData = filteredRockets.value.map((d) => ({
    ...d,
    heightValue: getHeightValue(d),
  }));

  // Escalas
  const x = d3
    .scaleBand()
    .domain(chartData.map((d) => d.name))
    .range([0, width])
    .padding(0.2);

  const maxHeight = d3.max(chartData, (d) => d.heightValue) || 100;
  const y = d3
    .scaleLinear()
    .domain([0, maxHeight + 10])
    .range([height, 0]);

  // Ejes
  svg
    .append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x))
    .selectAll("text")
    .attr("transform", "rotate(-15)")
    .style("text-anchor", "end")
    .style("fill", "#80deea");

  svg.append("g").call(d3.axisLeft(y).ticks(5)).style("color", "#80deea");

  // Etiqueta eje Y
  svg
    .append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", 0 - margin.left)
    .attr("x", 0 - height / 2)
    .attr("dy", "1em")
    .style("text-anchor", "middle")
    .style("fill", "#80deea")
    .text("Height (m)");

  // Barras
  svg
    .selectAll(".bar")
    .data(chartData)
    .enter()
    .append("rect")
    .attr("class", "bar")
    .attr("x", (d) => x(d.name) || 0)
    .attr("y", (d) => y(d.heightValue))
    .attr("width", x.bandwidth())
    .attr("height", (d) => height - y(d.heightValue))
    .attr("fill", (d) => (d.active ? "#00e6ff" : "#4a6fa5"))
    .attr("rx", 4)
    .attr("ry", 4);

  // Etiquetas de valor
  svg
    .selectAll(".label")
    .data(chartData)
    .enter()
    .append("text")
    .attr("class", "label")
    .attr("x", (d) => (x(d.name) || 0) + x.bandwidth() / 2)
    .attr("y", (d) => y(d.heightValue) - 5)
    .attr("text-anchor", "middle")
    .style("fill", "#ffffff")
    .style("font-size", "12px")
    .text((d) => (d.heightValue ? `${d.heightValue.toFixed(1)}m` : "N/A"));
}
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
  display: flex;
  flex-direction: column;
}

.view-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  position: relative;
  flex-shrink: 0;
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
  width: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 25px;
  padding: 10px;
  min-height: 0;
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

/* Secciones */
.timeline-section,
.rockets-section,
.d3-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 10px;
}

.section-icon {
  font-size: 1.8rem;
  color: #00e6ff;
  text-shadow: 0 0 10px rgba(0, 231, 255, 0.7);
}

.section-header h2 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
  letter-spacing: 1px;
  color: #80deea;
  text-transform: uppercase;
}

/* Contenedores */
.timeline-container,
.chart-container,
.d3-chart-container {
  background: rgba(16, 22, 58, 0.5);
  border-radius: 16px;
  border: 1px solid rgba(0, 231, 255, 0.2);
  padding: 20px;
  box-shadow: 0 0 30px rgba(0, 255, 255, 0.1);
  overflow: hidden;
  position: relative;
}

.timeline-container {
  min-height: 400px;
  display: block;
}

.chart-container,
.d3-chart-container {
  flex: 1;
  min-height: 400px;
}

.d3-chart {
  width: 100%;
  height: 300px;
}

/* Filtros */
.filters-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.filter-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-button {
  padding: 12px 20px;
  border-radius: 30px;
  border: 1px solid rgba(0, 231, 255, 0.3);
  background: rgba(16, 22, 58, 0.6);
  color: #d0f0ff;
  font-family: "Orbitron", sans-serif;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(6px);
  box-shadow: 0 0 10px rgba(0, 231, 255, 0.2);
}

.filter-button:hover {
  background: rgba(0, 231, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 0 15px rgba(0, 231, 255, 0.4);
}

.filter-button.active {
  background: rgba(0, 231, 255, 0.3);
  box-shadow: 0 0 15px rgba(0, 231, 255, 0.6);
  border-color: #00e6ff;
}

@media (min-width: 992px) {
  .dashboard-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto 1fr;
    gap: 25px;
    height: calc(100vh - 150px);
  }

  .filters-container {
    grid-column: 1 / span 2;
    flex-direction: row;
  }

  .search-box {
    flex: 1;
  }

  .filter-buttons {
    align-self: center;
  }

  .timeline-section {
    grid-column: 1;
    grid-row: 2;
    height: 100%;
  }
  .rockets-section {
    grid-column: 2;
    grid-row: 2;
    height: 100%;
  }

  .d3-section {
    grid-column: 1 / span 2;
    grid-row: 3;
  }

  .timeline-container {
    min-height: 0;
    height: 100%;
    display: flex;
  }

  .chart-container,
  .d3-chart-container {
    min-height: 0;
    height: 100%;
    position: relative;
  }
}

/* Buscador */
.search-box {
  background: rgba(10, 15, 40, 0.6);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 16px;
  padding: 15px;
  backdrop-filter: blur(6px);
}

.search-input {
  width: 100%;
  padding: 14px 20px;
  border-radius: 14px;
  border: 1px solid rgba(0, 255, 255, 0.3);
  background: rgba(0, 0, 0, 0.4);
  color: white;
  font-size: 1.1rem;
  outline: none;
  font-family: "Orbitron", sans-serif;
  letter-spacing: 1px;
  transition: all 0.3s ease;
}

.search-input:focus {
  border-color: #00fff7;
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.7);
  background: rgba(0, 0, 0, 0.6);
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

  .section-header h2 {
    font-size: 1.2rem;
  }

  .search-input {
    padding: 12px 16px;
    font-size: 1rem;
  }

  .timeline-container {
    height: 250px;
  }

  .chart-container,
  .d3-chart-container {
    min-height: 350px;
  }

  .filter-button {
    padding: 10px 15px;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .dashboard-content {
    padding: 5px;
    gap: 15px;
  }

  .section-header h2 {
    font-size: 1.1rem;
  }

  .timeline-container,
  .chart-container,
  .d3-chart-container {
    padding: 15px;
    border-radius: 14px;
  }

  .timeline-container {
    height: 220px;
  }

  .chart-container,
  .d3-chart-container {
    min-height: 300px;
  }
}
</style>

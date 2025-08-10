<template>
  <div ref="chartContainer" class="launch-timeline"></div>
</template>

<script setup lang="ts">
import * as d3 from "d3";
import { ref, onMounted, watch, onUnmounted } from "vue";
import { useSpaceX } from "../composables/useSpaceX";

interface LaunchData {
  year: string; // "2006"
  count: number;
}

const props = defineProps<{
  /** Altura fija opcional. Si no se pasa, usa la altura real del contenedor. */
  height?: number;
  /** Año inicial del timeline (default: 2006). */
  startYear?: number;
  /** Año final del timeline (default: año actual). */
  endYear?: number;
}>();

const chartContainer = ref<HTMLElement | null>(null);
const { fetchData } = useSpaceX();
const launchData = ref<LaunchData[]>([]);

// --- Helpers ---
let resizeObserver: ResizeObserver | null = null;

const getHeight = () => {
  return props.height ?? chartContainer.value?.clientHeight ?? 300;
};

/** Convierte lanzamientos crudos a {year, count} y densifica el rango de años */
const toDenseYearCounts = (launches: any[]): LaunchData[] => {
  const counts: Record<string, number> = {};

  for (const launch of launches ?? []) {
    const y = launch?.date_utc ? String(launch.date_utc).substring(0, 4) : null;
    if (y && /^\d{4}$/.test(y)) {
      counts[y] = (counts[y] || 0) + 1;
    }
  }

  const yearsInData = Object.keys(counts).map((y) => +y);
  const defaultStart = 2006; // primer lanzamiento de SpaceX
  const defaultEnd = new Date().getFullYear();

  const start =
    props.startYear ??
    (yearsInData.length ? Math.min(...yearsInData) : defaultStart);
  const end =
    props.endYear ??
    (yearsInData.length ? Math.max(...yearsInData) : defaultEnd);

  const dense: LaunchData[] = [];
  for (let y = start; y <= end; y++) {
    const key = String(y);
    dense.push({ year: key, count: counts[key] ?? 0 });
  }
  return dense;
};

const loadData = async () => {
  try {
    const response = await fetchData<{ data: any[] }>("/api/launches");
    if (response?.data) {
      launchData.value = toDenseYearCounts(response.data);
      return;
    }
  } catch (err) {
    console.error("Error loading launch data", err);
  }
  // Fallback mínimo si la API falla o viene vacía (también densificado)
  launchData.value = toDenseYearCounts([
    { date_utc: "2020-01-01T00:00:00.000Z" },
    { date_utc: "2020-02-01T00:00:00.000Z" },
    // 2021 (31)
    ...Array.from({ length: 31 }, () => ({
      date_utc: "2021-01-01T00:00:00.000Z",
    })),
    // 2022 (61)
    ...Array.from({ length: 61 }, () => ({
      date_utc: "2022-01-01T00:00:00.000Z",
    })),
    // 2023 (96)
    ...Array.from({ length: 96 }, () => ({
      date_utc: "2023-01-01T00:00:00.000Z",
    })),
  ]);
};

const drawChart = () => {
  if (!chartContainer.value || launchData.value.length === 0) return;

  // Limpiar contenedor
  d3.select(chartContainer.value).selectAll("*").remove();

  // Medidas del lienzo
  const width = chartContainer.value.clientWidth;
  const height = getHeight();
  const margin = { top: 20, right: 30, bottom: 40, left: 50 };
  const innerW = Math.max(0, width - margin.left - margin.right);
  const innerH = Math.max(0, height - margin.top - margin.bottom);

  const svg = d3
    .select(chartContainer.value)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  // Escalas
  const years = launchData.value.map((d) => d.year);
  const x = d3
    .scaleBand<string>()
    .domain(years)
    .range([0, innerW])
    .padding(0.1);

  const yMax = (d3.max(launchData.value, (d) => d.count) ?? 1) * 1.2;
  const y = d3.scaleLinear().domain([0, yMax]).nice().range([innerH, 0]);

  // Ejes (reducimos etiquetas si hay muchos años)
  const step = years.length > 20 ? 2 : 1; // muestra 1 de cada 2 si es largo
  const xAxis = d3
    .axisBottom(x)
    .tickValues(years.filter((_, i) => i % step === 0));
  const yAxis = d3.axisLeft(y).ticks(5);

  svg
    .append("g")
    .attr("class", "x-axis")
    .attr("transform", `translate(0,${innerH})`)
    .call(xAxis)
    .selectAll("text")
    .style("text-anchor", "middle")
    .attr("fill", "#80deea");

  svg
    .append("g")
    .attr("class", "y-axis")
    .call(yAxis)
    .selectAll("text")
    .attr("fill", "#80deea");

  // Línea
  const line = d3
    .line<LaunchData>()
    .x((d) => (x(d.year) ?? 0) + x.bandwidth() / 2)
    .y((d) => y(d.count))
    .curve(d3.curveMonotoneX);

  svg
    .append("path")
    .datum(launchData.value)
    .attr("fill", "none")
    .attr("stroke", "#00e6ff")
    .attr("stroke-width", 3)
    .attr("d", line)
    .style("filter", "url(#line-glow)");

  // Puntos
  svg
    .selectAll(".dot")
    .data(launchData.value)
    .enter()
    .append("circle")
    .attr("class", "dot")
    .attr("cx", (d) => (x(d.year) ?? 0) + x.bandwidth() / 2)
    .attr("cy", (d) => y(d.count))
    .attr("r", 6)
    .attr("fill", "#00e6ff")
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 2)
    .style("filter", "url(#point-glow)");

  // Etiquetas (solo para puntos > 0 para no saturar)
  svg
    .selectAll(".label")
    .data(launchData.value.filter((d) => d.count > 0))
    .enter()
    .append("text")
    .attr("class", "label")
    .attr("x", (d) => (x(d.year) ?? 0) + x.bandwidth() / 2)
    .attr("y", (d) => y(d.count) - 15)
    .attr("text-anchor", "middle")
    .attr("fill", "#00e6ff")
    .attr("font-weight", "bold")
    .text((d) => d.count);

  // Filtros de brillo
  const defs = svg.append("defs");

  const glowFilter = defs
    .append("filter")
    .attr("id", "line-glow")
    .attr("width", "150%")
    .attr("height", "150%");
  glowFilter
    .append("feGaussianBlur")
    .attr("stdDeviation", "3.5")
    .attr("result", "coloredBlur");
  const feMerge = glowFilter.append("feMerge");
  feMerge.append("feMergeNode").attr("in", "coloredBlur");
  feMerge.append("feMergeNode").attr("in", "SourceGraphic");

  const pointFilter = defs
    .append("filter")
    .attr("id", "point-glow")
    .attr("width", "150%")
    .attr("height", "150%");
  pointFilter
    .append("feGaussianBlur")
    .attr("stdDeviation", "2.5")
    .attr("result", "coloredBlur");
  const pointMerge = pointFilter.append("feMerge");
  pointMerge.append("feMergeNode").attr("in", "coloredBlur");
  pointMerge.append("feMergeNode").attr("in", "SourceGraphic");
};

// --- Lifecycle ---
onMounted(async () => {
  await loadData();
  drawChart();

  if (window.ResizeObserver && chartContainer.value) {
    resizeObserver = new ResizeObserver(() => drawChart());
    resizeObserver.observe(chartContainer.value);
  }
  window.addEventListener("resize", drawChart);
});

onUnmounted(() => {
  window.removeEventListener("resize", drawChart);
  if (resizeObserver) resizeObserver.disconnect();
});

watch(launchData, () => drawChart());
</script>

<style scoped>
.launch-timeline {
  width: 100%;
  height: 100%;
  min-height: 300px;
  background: rgba(5, 10, 30, 0.3);
  border-radius: 12px;
  padding: 15px;
}

:deep(.x-axis path),
:deep(.y-axis path) {
  stroke: rgba(0, 231, 255, 0.3);
}

:deep(.x-axis line),
:deep(.y-axis line) {
  stroke: rgba(0, 231, 255, 0.2);
}
</style>

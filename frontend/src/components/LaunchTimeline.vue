<template>
  <div ref="chartContainer" class="launch-timeline"></div>
</template>

<script setup lang="ts">
import * as d3 from "d3";
import { ref, onMounted, watch } from "vue";
import { useSpaceX } from "../composables/useSpaceX";

interface LaunchData {
  year: string;
  count: number;
}

const props = defineProps<{
  height?: number;
}>();

const chartContainer = ref<HTMLElement | null>(null);
const { fetchData } = useSpaceX();
const launchData = ref<LaunchData[]>([]);

// Procesar datos de lanzamientos para timeline
const processLaunchesForTimeline = (launches: any[]): LaunchData[] => {
  const yearCounts: Record<string, number> = {};

  launches.forEach((launch) => {
    if (launch.date_utc) {
      const year = launch.date_utc.substring(0, 4);
      yearCounts[year] = (yearCounts[year] || 0) + 1;
    }
  });

  return Object.entries(yearCounts)
    .map(([year, count]) => ({ year, count }))
    .sort((a, b) => a.year.localeCompare(b.year));
};

const loadData = async () => {
  try {
    const response = await fetchData<{ data: any[] }>("/api/launches");

    if (response && response.data) {
      launchData.value = processLaunchesForTimeline(response.data);
    } else {
      // Fallback mínimo si no hay datos
      launchData.value = [
        { year: "2020", count: 26 },
        { year: "2021", count: 31 },
        { year: "2022", count: 61 },
        { year: "2023", count: 96 },
      ];
    }
  } catch (error) {
    console.error("Error loading launch data", error);
    // Fallback para mantener funcionalidad
    launchData.value = [
      { year: "2020", count: 26 },
      { year: "2021", count: 31 },
      { year: "2022", count: 61 },
      { year: "2023", count: 96 },
    ];
  }
};

const drawChart = () => {
  if (!chartContainer.value || launchData.value.length === 0) return;

  // Limpiar contenedor
  d3.select(chartContainer.value).selectAll("*").remove();

  // Configuración del gráfico
  const width = chartContainer.value.clientWidth;
  const height = props.height || 300;
  const margin = { top: 20, right: 30, bottom: 40, left: 50 };

  const svg = d3
    .select(chartContainer.value)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  // Escalas
  const x = d3
    .scaleBand()
    .domain(launchData.value.map((d) => d.year))
    .range([0, width - margin.left - margin.right])
    .padding(0.1);

  const y = d3
    .scaleLinear()
    .domain([0, d3.max(launchData.value, (d) => d.count)! * 1.2])
    .range([height - margin.top - margin.bottom, 0]);

  // Ejes
  const xAxis = d3.axisBottom(x);
  const yAxis = d3.axisLeft(y).ticks(5);

  svg
    .append("g")
    .attr("class", "x-axis")
    .attr("transform", `translate(0,${height - margin.top - margin.bottom})`)
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
    .x((d) => x(d.year)! + x.bandwidth() / 2)
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
    .attr("cx", (d) => x(d.year)! + x.bandwidth() / 2)
    .attr("cy", (d) => y(d.count))
    .attr("r", 6)
    .attr("fill", "#00e6ff")
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 2)
    .style("filter", "url(#point-glow)");

  // Etiquetas
  svg
    .selectAll(".label")
    .data(launchData.value)
    .enter()
    .append("text")
    .attr("class", "label")
    .attr("x", (d) => x(d.year)! + x.bandwidth() / 2)
    .attr("y", (d) => y(d.count) - 15)
    .attr("text-anchor", "middle")
    .attr("fill", "#00e6ff")
    .attr("font-weight", "bold")
    .text((d) => d.count);

  // Filtro de brillo
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

onMounted(async () => {
  await loadData();
  drawChart();
  window.addEventListener("resize", drawChart);
});

watch(launchData, () => {
  drawChart();
});
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

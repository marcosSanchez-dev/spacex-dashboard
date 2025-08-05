<template>
  <div class="pie-container">
    <svg ref="svgRef" :width="width" :height="height" class="glow-chart"></svg>
    <div v-if="total > 0" class="stats-overlay">
      <div class="stat success">✓ {{ success }} ({{ successPercent }}%)</div>
      <div class="stat failure">✕ {{ failure }} ({{ failurePercent }}%)</div>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-ignore
import * as d3 from "d3";
import { ref, onMounted, watch, computed } from "vue";

const props = defineProps({
  success: { type: Number, default: 0 },
  failure: { type: Number, default: 0 },
});

const svgRef = ref<SVGSVGElement | null>(null);
const width = 350;
const height = 350;
const radius = Math.min(width, height) / 2 - 20;

// Calcula porcentajes
const total = computed(() => props.success + props.failure);
const successPercent = computed(() =>
  total.value ? Math.round((props.success / total.value) * 100) : 0
);
const failurePercent = computed(() =>
  total.value ? Math.round((props.failure / total.value) * 100) : 0
);

// Animación de entrada
let initialAnimationComplete = ref(false);

const drawChart = () => {
  if (!svgRef.value) return;

  const data = [
    { label: "Success", value: props.success, color: "#00ff9d" },
    { label: "Failure", value: props.failure, color: "#ff0055" },
  ];

  // Limpiar SVG
  d3.select(svgRef.value).selectAll("*").remove();

  const svg = d3.select(svgRef.value);
  const g = svg
    .append("g")
    .attr("transform", `translate(${width / 2}, ${height / 2})`);

  // Filtro para efecto glow
  const defs = svg.append("defs");
  const glowFilter = defs
    .append("filter")
    .attr("id", "pie-glow")
    .attr("width", "150%")
    .attr("height", "150%");

  glowFilter
    .append("feGaussianBlur")
    .attr("stdDeviation", "3.5")
    .attr("result", "coloredBlur");

  const feMerge = glowFilter.append("feMerge");
  feMerge.append("feMergeNode").attr("in", "coloredBlur");
  feMerge.append("feMergeNode").attr("in", "SourceGraphic");

  // Crear gráfico de pastel
  const pie = d3
    .pie<any>()
    .value((d) => d.value)
    .sort(null);
  const arc = d3
    .arc<any>()
    .innerRadius(radius * 0.5)
    .outerRadius(radius)
    .cornerRadius(8);

  const arcs = g
    .selectAll(".arc")
    .data(pie(data))
    .enter()
    .append("g")
    .attr("class", "arc");

  // Animación de entrada
  const arcTween = (d: any) => {
    const i = d3.interpolate(d.startAngle + 0.1, d.endAngle);
    return (t: number) => {
      d.endAngle = i(t);
      return arc(d);
    };
  };

  arcs
    .append("path")
    .attr("fill", (d) => d.data.color)
    .attr("d", arc)
    .attr("stroke", "#0a0e29")
    .attr("stroke-width", 2)
    .style("filter", "url(#pie-glow)")
    .style("opacity", 0)
    .transition()
    .duration(1200)
    .delay((d, i) => i * 300)
    .attrTween("d", arcTween)
    .style("opacity", 1);

  // Animación para el centro (donut hole)
  if (initialAnimationComplete.value) {
    g.append("circle")
      .attr("r", radius * 0.5)
      .attr("fill", "#0a0e29")
      .attr("stroke", "rgba(0, 231, 255, 0.2)")
      .attr("stroke-width", 1);
  } else {
    g.append("circle")
      .attr("r", 0)
      .attr("fill", "#0a0e29")
      .transition()
      .duration(1000)
      .delay(800)
      .attr("r", radius * 0.5)
      .on("end", () => (initialAnimationComplete.value = true));
  }

  // Texto central animado
  if (total.value > 0) {
    const centerText = g
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "0.35em")
      .attr("fill", "#80deea")
      .attr("font-weight", "bold")
      .attr("font-size", "18px")
      .style("opacity", 0);

    centerText
      .transition()
      .duration(800)
      .delay(1200)
      .style("opacity", 1)
      .text(`${successPercent.value}% Success`);
  }
};

onMounted(() => {
  drawChart();
  setTimeout(() => (initialAnimationComplete.value = true), 1500);
});

watch(
  () => [props.success, props.failure],
  () => {
    if (initialAnimationComplete.value) {
      drawChart();
    }
  }
);
</script>

<style scoped>
.pie-container {
  position: relative;
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.glow-chart {
  filter: drop-shadow(0 0 8px rgba(0, 231, 255, 0.3));
}

.stats-overlay {
  position: absolute;
  bottom: 20px;
  display: flex;
  gap: 30px;
}

.stat {
  padding: 8px 15px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  backdrop-filter: blur(5px);
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  gap: 5px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.success {
  color: #00ff9d;
  border: 1px solid rgba(0, 255, 157, 0.3);
}

.failure {
  color: #ff0055;
  border: 1px solid rgba(255, 0, 85, 0.3);
}
</style>

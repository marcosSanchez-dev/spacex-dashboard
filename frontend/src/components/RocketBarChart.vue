<template>
  <svg ref="svgRef" :width="width" :height="height"></svg>
</template>

<script setup lang="ts">
// @ts-ignore
import * as d3 from "d3";
import { ref, onMounted, watch } from "vue";

const props = defineProps<{
  data: Array<{ name: string; mass: number }>;
}>();

const svgRef = ref<SVGSVGElement | null>(null);
const width = 500;
const height = 300;

const drawChart = () => {
  const margin = { top: 20, right: 20, bottom: 30, left: 60 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  const svg = d3.select(svgRef.value);
  svg.selectAll("*").remove(); // limpia

  // ⚡ Gradiente
  const defs = svg.append("defs");
  const gradient = defs
    .append("linearGradient")
    .attr("id", "barGradient")
    .attr("x1", "0%")
    .attr("y1", "0%")
    .attr("x2", "0%")
    .attr("y2", "100%");

  gradient.append("stop").attr("offset", "0%").attr("stop-color", "#00f2ff"); // color eléctrico

  gradient.append("stop").attr("offset", "100%").attr("stop-color", "#005577"); // más oscuro

  const g = svg
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3
    .scaleBand()
    .domain(props.data.map((d: any) => d.name))
    .range([0, innerWidth])
    .padding(0.1);

  const y = d3
    .scaleLinear()
    .domain([0, d3.max(props.data, (d: any) => d.mass) || 0])
    .range([innerHeight, 0]);

  // ✨ Barras animadas
  g.selectAll(".bar")
    .data(props.data)
    .enter()
    .append("rect")
    .attr("class", "bar")
    .attr("x", (d: any) => x(d.name)!)
    .attr("y", innerHeight)
    .attr("width", x.bandwidth())
    .attr("height", 0)
    .attr("fill", "url(#barGradient)")
    .transition()
    .duration(800)
    .attr("y", (d: any) => y(d.mass))
    .attr("height", (d: any) => innerHeight - y(d.mass));

  // Ejes
  g.append("g")
    .attr("transform", `translate(0,${innerHeight})`)
    .call(d3.axisBottom(x));

  g.append("g").call(d3.axisLeft(y));
};

onMounted(drawChart);
watch(() => props.data, drawChart);
</script>

<style scoped>
text {
  fill: #00ffff;
  font-family: "Segoe UI", sans-serif;
  font-size: 12px;
  text-shadow: 0 0 4px #00ffff;
}
</style>

<template>
  <svg ref="svgRef" :width="width" :height="height"></svg>
</template>

<script setup lang="ts">
import * as d3 from "d3";
import { ref, onMounted, watch } from "vue";

const props = defineProps<{
  success: number;
  failure: number;
}>();

const svgRef = ref<SVGSVGElement | null>(null);
const width = 300;
const height = 300;

const drawChart = () => {
  const data = [
    { label: "Success", value: props.success },
    { label: "Failure", value: props.failure },
  ];

  const radius = Math.min(width, height) / 2;
  const svg = d3
    .select(svgRef.value)
    .attr("width", width)
    .attr("height", height)
    .selectAll("*")
    .remove();

  const g = d3
    .select(svgRef.value)
    .append("g")
    .attr("transform", `translate(${width / 2}, ${height / 2})`);

  const pie = d3.pie<any>().value((d) => d.value);
  const arc = d3.arc<any>().innerRadius(0).outerRadius(radius);
  const color = d3
    .scaleOrdinal()
    .domain(data.map((d) => d.label))
    .range(["#4caf50", "#f44336"]);

  const arcs = g.selectAll("arc").data(pie(data)).enter().append("g");

  arcs
    .append("path")
    .attr("d", arc)
    .attr("fill", (d) => color(d.data.label) as string);

  arcs
    .append("text")
    .attr("transform", (d) => `translate(${arc.centroid(d)})`)
    .attr("text-anchor", "middle")
    .attr("font-size", "14px")
    .text((d) => `${d.data.label}: ${d.data.value}`);
};

onMounted(drawChart);
watch(() => [props.success, props.failure], drawChart);
</script>

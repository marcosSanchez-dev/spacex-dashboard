<template>
  <div>
    <h1>Rockets</h1>
    <RocketBarChart :data="formattedRockets" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useSpaceX } from "../composables/useSpaceX";
import RocketBarChart from "../components/RocketBarChart.vue";

const rockets = ref([]);
const { fetchData } = useSpaceX();

onMounted(async () => {
  rockets.value = (await fetchData("/api/rockets")) || [];
});

const formattedRockets = computed(() =>
  rockets.value.map((r: any) => ({
    name: r.name,
    mass: r.mass,
  }))
);
</script>

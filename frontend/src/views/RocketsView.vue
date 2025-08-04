<template>
  <div>
    <h1>Rockets</h1>
    <ul v-if="rockets.length">
      <li v-for="rocket in rockets" :key="rocket.name">
        <strong>{{ rocket.name }}</strong> - {{ rocket.height }}m -
        {{ rocket.mass }}kg - ${{ rocket.cost }}
      </li>
    </ul>
    <p v-else>Cargando cohetes...</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useSpaceX } from "../composables/useSpaceX";

const rockets = ref([]);
const { fetchData } = useSpaceX();

onMounted(async () => {
  rockets.value = (await fetchData("/api/rockets")) || [];
});
</script>

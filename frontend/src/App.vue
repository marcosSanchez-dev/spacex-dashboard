<template>
  <div class="container">
    <nav>
      <RouterLink to="/">Dashboard</RouterLink> |
      <RouterLink to="/rockets">Rockets</RouterLink> |
      <RouterLink to="/starlink">Starlink</RouterLink>
    </nav>
    <hr />
    <RouterView />
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from "vue-router";
</script>

<style scoped>
.container {
  font-family: Arial, sans-serif;
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}
nav {
  margin-bottom: 12px;
}
</style>

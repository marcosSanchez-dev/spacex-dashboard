<template>
  <div class="app dark-theme">
    <nav>
      <RouterLink to="/">Dashboard</RouterLink>
      <RouterLink to="/rockets">Rockets</RouterLink>
      <RouterLink to="/starlink">Starlink</RouterLink>
    </nav>
    <RouterView />
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from "vue-router";
</script>

<style scoped>
.app {
  font-family: "Segoe UI", sans-serif;
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
  background-color: #0a0a0a;
  color: #e0e0e0;
  min-height: 100vh;
}

nav {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}

nav a {
  color: #00bcd4;
  text-decoration: none;
  font-weight: bold;
  transition: color 0.3s;
  text-shadow: 0 0 5px #00bcd4;
}

nav a:hover {
  color: #ffffff;
}
</style>

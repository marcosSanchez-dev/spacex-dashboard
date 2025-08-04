<template>
  <div>
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

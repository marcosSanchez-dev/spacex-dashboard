<template>
  <div class="app">
    <!-- Fondo espacial -->
    <div class="space-background"></div>

    <!-- Efectos visuales espaciales con CSS puro -->
    <div class="space-effects">
      <div class="stars"></div>
      <div class="twinkling"></div>
      <div class="clouds"></div>
    </div>

    <!-- Contenedor principal -->
    <div class="router-container">
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { RouterView } from "vue-router";
</script>

<style scoped>
.app {
  position: relative;
  min-height: 100vh;
  overflow-x: hidden;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
}

.space-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(
    ellipse at center,
    #0a0e2a 0%,
    #1a1f40 40%,
    #2a3256 100%
  );
  z-index: -3;
}

.space-effects {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -2;
  overflow: hidden;
}

/* Estrellas generadas con CSS puro */
.stars {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 10% 20%, white 1px, transparent 1px),
    radial-gradient(circle at 20% 30%, white 1px, transparent 1px),
    radial-gradient(circle at 30% 40%, white 1px, transparent 1px);
  background-size: 300px 300px;
  background-position: 0 0;
  animation: move-stars 200s linear infinite;
}

/* Nebulosas con gradientes CSS */
.clouds {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(
      circle at 20% 30%,
      rgba(157, 78, 221, 0.3),
      transparent 30%
    ),
    radial-gradient(circle at 80% 70%, rgba(0, 231, 255, 0.2), transparent 30%);
  animation: move-clouds 150s linear infinite;
  opacity: 0.2;
}

@keyframes move-stars {
  from {
    background-position: 0 0;
  }
  to {
    background-position: -1000px 500px;
  }
}

@keyframes move-clouds {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(-100%);
  }
}

.router-container {
  position: relative;
  z-index: 5;
}
</style>

<style>
/* Estilos globales */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body {
  height: 100%;
  overflow-x: hidden;
  background-color: #000;
}

/* Scrollbar personalizada */
::-webkit-scrollbar {
  width: 10px;
}

::-webkit-scrollbar-track {
  background: rgba(10, 14, 41, 0.5);
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 231, 255, 0.3);
  border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 231, 255, 0.5);
}
</style>

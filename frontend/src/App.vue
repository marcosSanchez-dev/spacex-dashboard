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

    <!-- Botones de control de audio -->
    <div class="audio-controls">
      <button class="music-toggle" @click="toggleMusic">
        <span v-if="!isMuted">🔊</span>
        <span v-else>🔇</span>
      </button>
      <button class="sound-effects-toggle" @click="toggleSoundEffects">
        <span v-if="soundEffectsEnabled">🎵</span>
        <span v-else>🔕</span>
      </button>
    </div>

    <!-- Navegación con estilo espacial -->
    <nav class="space-nav">
      <RouterLink to="/" class="nav-link" @click="playTransitionSound">
        <span class="nav-icon">📊</span>
        <span class="nav-text">Dashboard</span>
      </RouterLink>

      <RouterLink to="/rockets" class="nav-link" @click="playTransitionSound">
        <span class="nav-icon">🚀</span>
        <span class="nav-text">Rockets</span>
      </RouterLink>

      <RouterLink to="/starlink" class="nav-link" @click="playTransitionSound">
        <span class="nav-icon">🛰️</span>
        <span class="nav-text">Starlink</span>
      </RouterLink>
    </nav>

    <!-- Contenedor principal con transiciones -->
    <div class="router-container">
      <RouterView v-slot="{ Component }">
        <Transition name="zoom" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { RouterLink, RouterView } from "vue-router";

// Variables para control de audio (sistema simplificado)
const isMuted = ref(false);
const soundEffectsEnabled = ref(true);

function toggleMusic() {
  isMuted.value = !isMuted.value;
  // Implementación real iría aquí
  console.log("Music toggled:", isMuted.value ? "Muted" : "Unmuted");
}

function toggleSoundEffects() {
  soundEffectsEnabled.value = !soundEffectsEnabled.value;
  // Implementación real iría aquí
  console.log(
    "Sound effects toggled:",
    soundEffectsEnabled.value ? "Enabled" : "Disabled"
  );
}

function playTransitionSound() {
  if (soundEffectsEnabled.value) {
    // Implementación real iría aquí
    console.log("Playing transition sound");
  }
}
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

/* Estrellas centelleantes con pseudo-elementos */
.twinkling {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0.5;
}

.twinkling::before,
.twinkling::after {
  content: "";
  position: absolute;
  width: 1px;
  height: 1px;
  background: white;
  border-radius: 50%;
  box-shadow: 0 0 10px 2px rgba(255, 255, 255, 0.8),
    0 0 20px 4px rgba(255, 255, 255, 0.6);
  animation: twinkle 3s infinite ease-in-out;
}

.twinkling::before {
  top: 20%;
  left: 25%;
  animation-delay: 0.5s;
}

.twinkling::after {
  top: 60%;
  left: 70%;
  animation-delay: 1.5s;
}

@keyframes twinkle {
  0%,
  100% {
    opacity: 0.2;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1.5);
  }
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

.audio-controls {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 10px;
  z-index: 100;
}

.music-toggle,
.sound-effects-toggle {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: rgba(16, 22, 58, 0.6);
  border: 1px solid rgba(0, 231, 255, 0.3);
  color: #80deea;
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
  box-shadow: 0 0 10px rgba(0, 231, 255, 0.2);
}

.music-toggle:hover,
.sound-effects-toggle:hover {
  transform: scale(1.1);
  box-shadow: 0 0 15px rgba(0, 231, 255, 0.5);
}

.space-nav {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin: 40px 0 60px;
  padding: 15px;
  border-radius: 12px;
  background: rgba(16, 22, 58, 0.4);
  border: 1px solid rgba(0, 231, 255, 0.2);
  box-shadow: 0 0 15px rgba(0, 150, 255, 0.1);
  backdrop-filter: blur(5px);
  position: relative;
  z-index: 10;
}

.nav-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  padding: 12px 20px;
  border-radius: 8px;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
  min-width: 120px;
}

.nav-link::before {
  content: "";
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #00e6ff, #9d4edd, #00e6ff);
  z-index: -1;
  border-radius: 10px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.nav-link:hover::before {
  opacity: 0.3;
}

.nav-icon {
  font-size: 2rem;
  margin-bottom: 8px;
  transition: transform 0.3s ease;
}

.nav-text {
  font-weight: 600;
  color: #80deea;
  letter-spacing: 1px;
  transition: color 0.3s ease;
}

.nav-link:hover .nav-icon {
  transform: translateY(-5px);
}

.nav-link:hover .nav-text {
  color: #ffffff;
}

.nav-link.router-link-active {
  background: rgba(157, 78, 221, 0.3);
  box-shadow: 0 0 15px rgba(157, 78, 221, 0.5);
}

.nav-link.router-link-active .nav-text {
  color: #ffffff;
  text-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
}

.router-container {
  position: relative;
  z-index: 5;
}

/* Transiciones de zoom */
.zoom-enter-active,
.zoom-leave-active {
  transition: all 0.6s cubic-bezier(0.68, -0.55, 0.27, 1.55);
}

.zoom-enter-from,
.zoom-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(20px);
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

<template>
  <div class="starlink-view">
    <h1 class="glow-title">🛰️ Starlink Network</h1>

    <transition name="fade">
      <div v-if="isLoading" class="loading-indicator">
        <div class="spinner"></div>
        <p>Initializing satellite network...</p>
      </div>
    </transition>

    <transition name="slide-fade">
      <div v-if="error" class="error-toast">
        ⚠️ {{ error }} <button @click="error = ''">✕</button>
      </div>
    </transition>

    <!-- Controles de órbita -->
    <div class="orbit-controls glow-box">
      <div class="filter-header">
        <span class="filter-icon">🌎</span>
        <h3>SATELLITE ORBITS</h3>
      </div>
      <div class="toggle-group">
        <button
          @click="activeOrbit = 'all'"
          :class="{ active: activeOrbit === 'all' }"
        >
          ALL SATELLITES
        </button>
        <button
          @click="activeOrbit = 'polar'"
          :class="{ active: activeOrbit === 'polar' }"
        >
          POLAR ORBITS
        </button>
        <button
          @click="activeOrbit = 'geo'"
          :class="{ active: activeOrbit === 'geo' }"
        >
          GEOSTATIONARY
        </button>
      </div>
      <div class="stats">
        <div class="stat">
          <div class="sat-icon active"></div>
          <span>{{ visibleSatellites }} / {{ satellites.length }} VISIBLE</span>
        </div>
      </div>
    </div>

    <!-- Contenedor del globo -->
    <div ref="globeContainer" class="globe-container"></div>
  </div>
</template>

<script setup lang="ts">
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { onMounted, onUnmounted, ref, watch, computed } from "vue";
import { useSpaceX } from "../composables/useSpaceX";

interface StarlinkSatellite {
  id: string;
  name: string;
  latitude: number | null;
  longitude: number | null;
  altitude_km: number | null;
  inclination_deg: number;
}

const satellites = ref<StarlinkSatellite[]>([]);
const globeContainer = ref<HTMLElement | null>(null);
const activeOrbit = ref<"all" | "polar" | "geo">("all");
const { fetchData, isLoading, error } = useSpaceX();

// Escena Three.js
let scene: THREE.Scene;
let camera: THREE.PerspectiveCamera;
let renderer: THREE.WebGLRenderer;
let controls: OrbitControls;
let earth: THREE.Mesh;
let satelliteGroup: THREE.Group;
const satObjects: THREE.Mesh[] = [];

onMounted(async () => {
  satellites.value =
    (await fetchData<StarlinkSatellite[]>("/api/starlink")) || [];
  initGlobe();
});

// Satélites visibles según filtro
const visibleSatellites = computed(() => {
  if (activeOrbit.value === "all") return satellites.value.length;

  return satellites.value.filter((sat) => {
    if (activeOrbit.value === "polar") {
      return sat.inclination_deg >= 85;
    } else {
      // geo
      return sat.inclination_deg <= 5;
    }
  }).length;
});

watch(activeOrbit, () => {
  updateSatelliteVisibility();
});

function initGlobe() {
  if (!globeContainer.value) return;

  // 1. Crear escena
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x000814);

  // 2. Crear cámara
  camera = new THREE.PerspectiveCamera(
    45,
    globeContainer.value.clientWidth / globeContainer.value.clientHeight,
    0.1,
    1000
  );
  camera.position.z = 3;

  // 3. Crear renderizador
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(
    globeContainer.value.clientWidth,
    globeContainer.value.clientHeight
  );
  renderer.setPixelRatio(window.devicePixelRatio);
  globeContainer.value.appendChild(renderer.domElement);

  // 4. Controles de órbita
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.rotateSpeed = 0.5;

  // 5. Crear Tierra
  createEarth();

  // 6. Crear satélites
  createSatellites();

  // 7. Iluminación
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
  scene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
  directionalLight.position.set(5, 3, 5);
  scene.add(directionalLight);

  // Luz para efecto de brillo
  const pointLight = new THREE.PointLight(0xffff00, 0.5, 100);
  pointLight.position.set(10, 10, 10);
  scene.add(pointLight);

  // 8. Animación
  animate();

  // 9. Manejar redimensionamiento
  window.addEventListener("resize", onWindowResize);
}

function createEarth() {
  // Textura de la Tierra
  const textureLoader = new THREE.TextureLoader();

  // Usar texturas base64 integradas como fallback
  const earthTexture = createFallbackTexture("#1a5c9e", "#0a4a36", "#d8d0c1");
  const bumpMap = createGradientTexture();
  const specularMap = createGradientTexture();

  const geometry = new THREE.SphereGeometry(1, 64, 64);
  const material = new THREE.MeshPhongMaterial({
    map: earthTexture,
    bumpMap: bumpMap,
    bumpScale: 0.05,
    specularMap: specularMap,
    specular: new THREE.Color(0x333333),
    shininess: 5,
  });

  earth = new THREE.Mesh(geometry, material);
  scene.add(earth);

  // Nubes (opcional)
  const cloudsMaterial = new THREE.MeshPhongMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 0.2,
  });

  const clouds = new THREE.Mesh(
    new THREE.SphereGeometry(1.01, 64, 64),
    cloudsMaterial
  );
  scene.add(clouds);
}

function createSatellites() {
  satelliteGroup = new THREE.Group();
  scene.add(satelliteGroup);

  // Crear geometría de satélite
  const geometry = new THREE.SphereGeometry(0.015, 8, 8);

  satellites.value.forEach((sat, index) => {
    // Si no hay datos de posición, generar posición simulada basada en inclinación
    const position = generateSatellitePosition(sat, index);

    const material = new THREE.MeshPhongMaterial({
      color: 0xffff00,
      emissive: 0xffff00,
      emissiveIntensity: 0.8,
      shininess: 100,
    });

    const satellite = new THREE.Mesh(geometry, material);
    satellite.position.copy(position);

    // Guardar datos para filtrado
    satellite.userData = {
      inclination: sat.inclination_deg,
      altitude: sat.altitude_km || 550,
    };

    satelliteGroup.add(satellite);
    satObjects.push(satellite);

    // Crear trayectoria orbital
    createOrbitPath(position.length(), sat.inclination_deg);
  });
}

function generateSatellitePosition(
  sat: StarlinkSatellite,
  index: number
): THREE.Vector3 {
  // Si tenemos datos reales, usarlos
  if (
    sat.latitude !== null &&
    sat.longitude !== null &&
    sat.altitude_km !== null
  ) {
    return latLonAltToVector3(
      sat.latitude,
      sat.longitude,
      sat.altitude_km / 6371
    );
  }

  // Generar posición simulada basada en inclinación
  const inclination = sat.inclination_deg;
  const altitude = sat.altitude_km || 550; // Altitud predeterminada para Starlink
  const altitudeNorm = altitude / 6371; // Normalizar por radio de la Tierra

  // Ángulo orbital basado en índice para distribución
  const orbitAngle = (index / satellites.value.length) * Math.PI * 2;

  // Calcular posición usando inclinación y ángulo orbital
  const x = Math.cos(orbitAngle) * (1 + altitudeNorm);
  const y =
    Math.sin((inclination * Math.PI) / 180) *
    Math.sin(orbitAngle) *
    (1 + altitudeNorm);
  const z = Math.sin(orbitAngle) * (1 + altitudeNorm);

  return new THREE.Vector3(x, y, z);
}

function createOrbitPath(radius: number, inclination: number) {
  const points = [];
  const segments = 100;

  for (let i = 0; i <= segments; i++) {
    const theta = (i / segments) * Math.PI * 2;
    const x = Math.cos(theta) * radius;
    const y =
      Math.sin((inclination * Math.PI) / 180) * Math.sin(theta) * radius;
    const z = Math.sin(theta) * radius;
    points.push(new THREE.Vector3(x, y, z));
  }

  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const material = new THREE.LineBasicMaterial({
    color: 0x444444,
    transparent: true,
    opacity: 0.3,
  });

  const orbit = new THREE.Line(geometry, material);
  scene.add(orbit);
}

function latLonAltToVector3(lat: number, lon: number, altNorm: number) {
  const phi = ((90 - lat) * Math.PI) / 180;
  const theta = ((lon + 180) * Math.PI) / 180;

  const radius = 1 + altNorm;

  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  );
}

function updateSatelliteVisibility() {
  satObjects.forEach((sat) => {
    const visible =
      activeOrbit.value === "all" ||
      (activeOrbit.value === "polar" && sat.userData.inclination >= 85) ||
      (activeOrbit.value === "geo" && sat.userData.inclination <= 5);

    sat.visible = visible;
  });
}

function animate() {
  requestAnimationFrame(animate);

  // Rotar la Tierra
  if (earth) {
    earth.rotation.y += 0.0005;
  }

  // Rotar satélites alrededor de la Tierra
  satelliteGroup.rotation.y += 0.001;

  // Animación de satélites
  satObjects.forEach((sat, index) => {
    sat.rotation.y += 0.01;
    sat.position.y = Math.sin(Date.now() * 0.001 + index) * 0.01;
  });

  controls.update();
  renderer.render(scene, camera);
}

function onWindowResize() {
  if (!globeContainer.value) return;

  camera.aspect =
    globeContainer.value.clientWidth / globeContainer.value.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(
    globeContainer.value.clientWidth,
    globeContainer.value.clientHeight
  );
}

// Funciones para generar texturas de fallback
function createFallbackTexture(
  color1: string,
  color2: string,
  color3: string
): THREE.Texture {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext("2d")!;

  // Crear un gradiente simple
  const gradient = ctx.createRadialGradient(128, 128, 0, 128, 128, 128);
  gradient.addColorStop(0, color1);
  gradient.addColorStop(0.5, color2);
  gradient.addColorStop(1, color3);

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 256, 256);

  return new THREE.CanvasTexture(canvas);
}

function createGradientTexture(): THREE.Texture {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext("2d")!;

  const gradient = ctx.createLinearGradient(0, 0, 256, 256);
  gradient.addColorStop(0, "#000000");
  gradient.addColorStop(1, "#ffffff");

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 256, 256);

  return new THREE.CanvasTexture(canvas);
}

onUnmounted(() => {
  window.removeEventListener("resize", onWindowResize);
  if (renderer) {
    renderer.dispose();
  }
});
</script>

<style scoped>
.starlink-view {
  background: radial-gradient(ellipse at center, #0a0e29 0%, #000814 70%);
  color: #e0f7fa;
  padding: 20px;
  min-height: 100vh;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  position: relative;
}

.glow-title {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 30px;
  text-shadow: 0 0 10px rgba(255, 255, 0, 0.5), 0 0 20px rgba(255, 255, 0, 0.3);
  letter-spacing: 2px;
}

.globe-container {
  width: 100%;
  height: 80vh;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 0 30px rgba(255, 255, 0, 0.1);
}

.orbit-controls {
  background: rgba(16, 22, 58, 0.6);
  border: 1px solid rgba(255, 255, 0, 0.3);
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 25px;
  backdrop-filter: blur(5px);
  max-width: 800px;
  margin: 0 auto 30px;
}

.filter-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.filter-header h3 {
  margin: 0;
  font-weight: 600;
  letter-spacing: 1px;
  color: #ffeb3b;
}

.toggle-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.toggle-group button {
  flex: 1;
  min-width: 120px;
  padding: 10px 15px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 0, 0.3);
  background: rgba(0, 0, 0, 0.4);
  color: #ffeb3b;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.toggle-group button:hover {
  background: rgba(255, 255, 0, 0.1);
  transform: translateY(-2px);
}

.toggle-group button.active {
  background: rgba(255, 255, 0, 0.3);
  border-color: #ffeb3b;
  box-shadow: 0 0 10px rgba(255, 255, 0, 0.3);
}

.stats {
  margin-top: 15px;
  display: flex;
  justify-content: center;
}

.stat {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 15px;
  border-radius: 20px;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 0, 0.3);
}

.sat-icon {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ffff00;
  box-shadow: 0 0 5px #ffff00;
}

/* Reutilizar estilos de spinner y error toast de vistas anteriores */
.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  gap: 15px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 0, 0.2);
  border-top: 4px solid #ffeb3b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.error-toast {
  background: rgba(255, 88, 88, 0.15);
  border: 1px solid rgba(255, 100, 100, 0.3);
  border-radius: 8px;
  padding: 12px 20px;
  margin: 15px auto;
  max-width: 500px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(5px);
  box-shadow: 0 0 15px rgba(255, 0, 0, 0.2);
}

.error-toast button {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 1.2rem;
}

/* Transiciones */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}
.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}
</style>

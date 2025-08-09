<template>
  <div class="starlink-view">
    <div class="view-header">
      <RouterLink to="/" class="back-button">
        <span class="back-icon">←</span>
        <span class="back-text">Dashboard</span>
      </RouterLink>
      <div class="logo-title">
        <img
          src="/img/logo.png"
          alt="SpaceX Mission Control"
          class="glow-logo"
        />
      </div>
    </div>

    <!-- Loader flotante -->
    <transition name="fade">
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-content">
          <div class="spinner"></div>
          <p>Initializing satellite network...</p>
        </div>
      </div>
    </transition>

    <transition name="slide-fade">
      <div v-if="error" class="error-toast">
        ⚠️ {{ error }} <button @click="error = ''">✕</button>
      </div>
    </transition>

    <div class="dashboard-content">
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
            <span
              >{{ visibleSatellites }} / {{ satellites.length }} VISIBLE</span
            >
          </div>
        </div>
      </div>

      <!-- Contenedor del globo -->
      <div ref="globeContainer" class="globe-container"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { onMounted, onUnmounted, ref, watch, computed } from "vue";
import { useSpaceX } from "../composables/useSpaceX";
import { RouterLink } from "vue-router";

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

// Misma función de generación de satélites demo que en DashboardView.vue
function generateDemoSatellites(count = 150): StarlinkSatellite[] {
  const fake = [];
  for (let i = 0; i < count; i++) {
    const inclination = i % 3 === 0 ? 90 : i % 3 === 1 ? 0 : 53;
    fake.push({
      id: `demo-${i}`,
      name: `DemoSat-${i}`,
      latitude: 0, // No se usa
      longitude: 0, // No se usa
      altitude_km: 500 + Math.random() * 300, // entre 500km y 800km
      inclination_deg: inclination,
    });
  }
  return fake;
}

onMounted(async () => {
  const response = await fetchData<{ data: StarlinkSatellite[] }>(
    "/api/starlink"
  );
  satellites.value = response?.data || [];

  // Usar siempre los mismos satélites demo que en DashboardView
  if (satellites.value.length === 0) {
    satellites.value = generateDemoSatellites(150);
  } else {
    // Combinar datos reales con demo para mantener consistencia visual
    const demoCount = Math.max(0, 150 - satellites.value.length);
    satellites.value = [
      ...satellites.value,
      ...generateDemoSatellites(demoCount),
    ];
  }

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
    100000
  );
  camera.position.set(0, 0, 4);

  // 3. Crear renderizador
  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
  });
  renderer.setSize(
    globeContainer.value.clientWidth,
    globeContainer.value.clientHeight
  );
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
  globeContainer.value.appendChild(renderer.domElement);

  // 4. Controles de órbita
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.rotateSpeed = 0.5;
  controls.enablePan = false;
  controls.enableZoom = true;
  controls.screenSpacePanning = false;
  controls.minDistance = 10;
  controls.maxDistance = 30;

  // 5. Crear Tierra
  createRealisticEarth();

  // 6. Crear satélites
  createSatellites();

  // 7. Iluminación
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
  scene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
  directionalLight.position.set(5, 3, 5);
  scene.add(directionalLight);

  // 8. Animación
  animate();

  // 9. Manejar redimensionamiento
  window.addEventListener("resize", onWindowResize);
}

async function createRealisticEarth() {
  try {
    const textureLoader = new THREE.TextureLoader();

    const texturePaths = {
      color: "textures/earth/color.jpg",
      bump: "textures/earth/bump.jpg",
      specular: "textures/earth/specular.jpg",
      clouds: "textures/earth/clouds.jpg",
    };

    // Cargar texturas
    const earthTexture = await textureLoader.loadAsync(texturePaths.color);
    const bumpMap = await textureLoader.loadAsync(texturePaths.bump);
    const specularMap = await textureLoader.loadAsync(texturePaths.specular);
    const cloudsTexture = await textureLoader.loadAsync(texturePaths.clouds);

    // Material para la Tierra
    const earthMaterial = new THREE.MeshPhongMaterial({
      map: earthTexture,
      bumpMap: bumpMap,
      bumpScale: 0.05,
      specularMap: specularMap,
      specular: new THREE.Color(0x333333),
      shininess: 15,
    });

    const earthGeometry = new THREE.SphereGeometry(1, 64, 64);
    earth = new THREE.Mesh(earthGeometry, earthMaterial);
    scene.add(earth);

    // Material para las nubes
    const cloudsMaterial = new THREE.MeshPhongMaterial({
      map: cloudsTexture,
      transparent: true,
      opacity: 0.8,
      depthWrite: false,
    });

    const cloudsGeometry = new THREE.SphereGeometry(1.005, 64, 64);
    const clouds = new THREE.Mesh(cloudsGeometry, cloudsMaterial);
    scene.add(clouds);

    // Crear atmósfera
    createAtmosphere();
  } catch (err) {
    console.error("Error loading Earth textures:", err);
    createBasicEarth();
  }
}

function createAtmosphere() {
  const atmosphereGeometry = new THREE.SphereGeometry(1.02, 32, 32);
  const atmosphereMaterial = new THREE.MeshPhongMaterial({
    color: 0x5588dd,
    transparent: true,
    opacity: 0.15,
    side: THREE.BackSide,
    shininess: 0,
  });

  const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
  scene.add(atmosphere);
}

function createBasicEarth() {
  const geometry = new THREE.SphereGeometry(1, 32, 32);
  const material = new THREE.MeshPhongMaterial({
    color: 0x1a5c9e,
    shininess: 5,
  });

  earth = new THREE.Mesh(geometry, material);
  scene.add(earth);
}

function createSatellites() {
  satelliteGroup = new THREE.Group();
  scene.add(satelliteGroup);

  // Crear geometría de satélite
  const geometry = new THREE.SphereGeometry(0.015, 6, 6);

  satellites.value.forEach((sat, index) => {
    let position: THREE.Vector3;
    const isDemo = sat.id.includes("demo");

    if (sat.inclination_deg <= 5) {
      // Satélites geoestacionarios
      const orbitAngle = (index / satellites.value.length) * Math.PI * 2;
      const altitude = sat.altitude_km || 35786;
      const orbitRadius = 1 + altitude / 6371;
      position = new THREE.Vector3(
        Math.cos(orbitAngle) * orbitRadius,
        0,
        Math.sin(orbitAngle) * orbitRadius
      );
    } else {
      // Otros satélites
      position = generateSatellitePosition(sat, index);
    }

    // Material con color diferente para demos
    const color = isDemo ? 0xff7700 : 0xffff00;
    const material = new THREE.MeshPhongMaterial({
      color: color,
      emissive: color,
      emissiveIntensity: 0.8,
      shininess: 100,
    });

    const satellite = new THREE.Mesh(geometry, material);
    satellite.position.copy(position);
    satellite.lookAt(new THREE.Vector3(0, 0, 0));

    // Guardar datos para filtrado
    satellite.userData = {
      inclination: sat.inclination_deg,
      altitude: sat.altitude_km || 550,
      isDemo: isDemo,
    };

    satelliteGroup.add(satellite);
    satObjects.push(satellite);
  });

  updateSatelliteVisibility();
}

function generateSatellitePosition(
  sat: StarlinkSatellite,
  index: number
): THREE.Vector3 {
  const inclination = sat.inclination_deg;
  const altitude = sat.altitude_km || 550;
  const altitudeNorm = altitude / 6371;
  const orbitAngle = (index / satellites.value.length) * Math.PI * 2;

  return new THREE.Vector3(
    Math.cos(orbitAngle) * (1 + altitudeNorm),
    Math.sin((inclination * Math.PI) / 180) *
      Math.sin(orbitAngle) *
      (1 + altitudeNorm),
    Math.sin(orbitAngle) * (1 + altitudeNorm)
  );
}

function updateSatelliteVisibility() {
  satObjects.forEach((sat) => {
    let visible = false;

    if (activeOrbit.value === "all") {
      visible = true;
    } else if (activeOrbit.value === "polar") {
      visible = sat.userData.inclination >= 85;
    } else if (activeOrbit.value === "geo") {
      visible = sat.userData.inclination <= 5;
    }

    // Mantener visibles los satélites de demostración en sus categorías
    if (sat.userData.isDemo) {
      if (activeOrbit.value === "polar" && sat.userData.inclination >= 85) {
        visible = true;
      } else if (activeOrbit.value === "geo" && sat.userData.inclination <= 5) {
        visible = true;
      }
    }

    sat.visible = visible;
  });
}

function animate() {
  requestAnimationFrame(animate);

  // Rotar la Tierra
  if (earth) {
    earth.rotation.y += 0.0005;
  }

  // Rotar satélites
  satelliteGroup.rotation.y += 0.001;

  // Animación de satélites (solo demos para rendimiento)
  satObjects.forEach((sat, index) => {
    if (sat.userData.isDemo) {
      const blink = Math.sin(Date.now() * 0.005 + index) * 0.5 + 0.5;
      (sat.material as THREE.MeshPhongMaterial).emissiveIntensity = blink * 0.8;
    }
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

onUnmounted(() => {
  window.removeEventListener("resize", onWindowResize);
  if (renderer) {
    renderer.dispose();
  }
});
</script>

<style scoped>
.starlink-view {
  background: radial-gradient(
    ellipse at center,
    #0a0f2c 0%,
    #141b3a 40%,
    #0b1d34 100%
  );
  color: #d0f0ff;
  padding: 15px;
  min-height: 100vh;
  font-family: "Orbitron", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  position: relative;
}

.view-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  position: relative;
}

.back-button {
  position: absolute;
  left: 0;
  display: flex;
  align-items: center;
  padding: 10px 15px;
  background: rgba(16, 22, 58, 0.6);
  border: 1px solid rgba(0, 231, 255, 0.3);
  border-radius: 30px;
  color: #d0f0ff;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  backdrop-filter: blur(6px);
  box-shadow: 0 0 15px rgba(0, 231, 255, 0.2);
  z-index: 10;
}

.back-button:hover {
  background: rgba(0, 231, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 0 20px rgba(0, 231, 255, 0.4);
}

.back-icon {
  margin-right: 8px;
  font-size: 1.2rem;
}

.logo-title {
  margin: 0 auto;
  text-align: center;
}

.glow-logo {
  max-width: 220px;
  height: auto;
  filter: drop-shadow(0 0 12px rgba(0, 255, 255, 0.75))
    drop-shadow(0 0 25px rgba(0, 150, 255, 0.5));
}

.dashboard-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
}

/* Loader flotante */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(10, 14, 41, 0.8);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(4px);
}

.loading-content {
  text-align: center;
}

.loading-overlay .spinner {
  width: 60px;
  height: 60px;
  border: 5px solid rgba(0, 231, 255, 0.3);
  border-top: 5px solid #00e6ff;
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
  margin: 0 auto 20px;
}

.loading-overlay p {
  font-size: 1.2rem;
  color: #00e6ff;
  text-shadow: 0 0 10px rgba(0, 231, 255, 0.7);
}

.globe-container {
  width: 100%;
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 0 30px rgba(0, 255, 255, 0.3);
  background: #000814;
  margin-top: 20px;
  flex: 1;
  min-height: 300px;
}

.orbit-controls {
  background: rgba(16, 22, 58, 0.6);
  border: 1px solid rgba(0, 231, 255, 0.3);
  border-radius: 12px;
  padding: 20px;
  backdrop-filter: blur(6px);
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
  color: #80deea;
  text-transform: uppercase;
}

.toggle-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
  margin-bottom: 15px;
}

.toggle-group button {
  flex: 1;
  min-width: 160px;
  padding: 12px 15px;
  border-radius: 8px;
  border: 1px solid rgba(0, 231, 255, 0.4);
  background: rgba(0, 20, 40, 0.6);
  color: #d0f0ff;
  cursor: pointer;
  font-weight: 600;
  letter-spacing: 1px;
  transition: all 0.25s ease;
  text-transform: uppercase;
  font-size: 0.9rem;
}

.toggle-group button:hover {
  background: rgba(0, 231, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 0 15px rgba(0, 231, 255, 0.4);
}

.toggle-group button.active {
  background: linear-gradient(
    45deg,
    rgba(0, 230, 255, 0.2),
    rgba(157, 78, 221, 0.2)
  );
  border-color: #00fff7;
  box-shadow: 0 0 15px rgba(0, 231, 255, 0.5);
  color: #ffffff;
}

.stats {
  display: flex;
  justify-content: center;
}

.stat {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  border-radius: 20px;
  background: rgba(0, 10, 30, 0.6);
  border: 1px solid rgba(0, 231, 255, 0.4);
  box-shadow: 0 0 15px rgba(0, 231, 255, 0.2);
  font-size: 1rem;
  font-weight: 500;
}

.sat-icon {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #00fff7;
  box-shadow: 0 0 8px #00fff7;
}

/* ERROR */
.error-toast {
  background: rgba(255, 88, 88, 0.15);
  border: 1px solid rgba(255, 100, 100, 0.3);
  border-radius: 8px;
  padding: 10px 15px;
  margin: 10px auto;
  max-width: 450px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(5px);
  box-shadow: 0 0 12px rgba(255, 0, 0, 0.2);
  font-size: 0.9rem;
  position: relative;
  z-index: 1001;
}

.error-toast button {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 1.1rem;
}

/* Animaciones */
@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* Transiciones */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
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

/* Responsive */
@media (max-width: 1200px) {
  .globe-container {
    height: 500px;
  }
}

@media (max-width: 768px) {
  .view-header {
    flex-direction: column;
    gap: 15px;
  }

  .back-button {
    position: static;
    align-self: flex-start;
  }

  .back-text {
    display: none;
  }

  .glow-logo {
    max-width: 180px;
  }

  .toggle-group button {
    min-width: 120px;
    padding: 10px 12px;
    font-size: 0.8rem;
  }
}
</style>

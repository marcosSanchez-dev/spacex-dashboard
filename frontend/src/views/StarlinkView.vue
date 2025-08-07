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
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
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
  const apiData = await fetchData<StarlinkSatellite[]>("/api/starlink");
  satellites.value = apiData || [];

  // Añadir satélites de demostración si hay pocos en ciertas categorías
  if (!hasEnoughPolarSats(satellites.value)) {
    addDemoSatellites("polar", 20);
  }

  if (!hasEnoughGeoSats(satellites.value)) {
    addDemoSatellites("geo", 15);
  }

  initGlobe();
});

// Verificar si hay suficientes satélites polares
function hasEnoughPolarSats(sats: StarlinkSatellite[]): boolean {
  return sats.filter((sat) => sat.inclination_deg >= 85).length > 5;
}

// Verificar si hay suficientes satélites geoestacionarios
function hasEnoughGeoSats(sats: StarlinkSatellite[]): boolean {
  return sats.filter((sat) => sat.inclination_deg <= 5).length > 5;
}

// Añadir satélites de demostración
function addDemoSatellites(type: "polar" | "geo", count: number) {
  const baseInclination = type === "polar" ? 85 : 0;

  for (let i = 0; i < count; i++) {
    const inclination = baseInclination + Math.random() * 5;

    satellites.value.push({
      id: `demo-${type}-${i}`,
      name: `DEMO ${type.toUpperCase()} ${i + 1}`,
      latitude: null,
      longitude: null,
      altitude_km: type === "geo" ? 35786 : 550,
      inclination_deg: inclination,
    });
  }
}

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

  // 2. Crear cámara - Ajustada para vista más amplia
  camera = new THREE.PerspectiveCamera(
    45,
    globeContainer.value.clientWidth / globeContainer.value.clientHeight,
    0.1,
    100000 // Rango extendido para ver satélites lejanos
  );
  camera.position.set(0, 0, 15); // Más alejado para ver todo

  // 3. Crear renderizador
  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    logarithmicDepthBuffer: true, // Mejor manejo de profundidad
  });
  renderer.setSize(
    globeContainer.value.clientWidth,
    globeContainer.value.clientHeight
  );
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  globeContainer.value.appendChild(renderer.domElement);

  // 4. Controles de órbita (solo rotación)
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.rotateSpeed = 0.5;

  // Configurar controles para solo rotación
  controls.enablePan = false; // Desactivar movimiento lateral
  controls.enableZoom = true; // Permitir zoom
  controls.screenSpacePanning = false;
  controls.minDistance = 10; // Evitar acercarse demasiado
  controls.maxDistance = 30; // Evitar alejarse demasiado

  // 5. Crear Tierra con textura realista
  createRealisticEarth();

  // 6. Crear satélites
  createSatellites();

  // 7. Iluminación mejorada
  const ambientLight = new THREE.AmbientLight(0xffffff, 1.0); // Más brillo
  scene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5); // Más intensidad
  directionalLight.position.set(5, 3, 5).normalize();
  scene.add(directionalLight);

  // Luz adicional para mejor contraste
  const backLight = new THREE.DirectionalLight(0xffffff, 0.5);
  backLight.position.set(-5, -1, -5).normalize();
  scene.add(backLight);

  // 8. Animación
  animate();

  // 9. Manejar redimensionamiento
  window.addEventListener("resize", onWindowResize);
}

async function createRealisticEarth() {
  try {
    const textureLoader = new THREE.TextureLoader();

    // Texturas de alta resolución de NASA (ruta corregida)
    const texturePaths = {
      color: "textures/earth/color.jpg", // Ruta corregida
      bump: "textures/earth/bump.jpg",
      specular: "textures/earth/specular.jpg",
      clouds: "textures/earth/clouds.jpg",
    };

    // Cargar texturas
    const earthTexture = await textureLoader.loadAsync(texturePaths.color);
    const bumpMap = await textureLoader.loadAsync(texturePaths.bump);
    const specularMap = await textureLoader.loadAsync(texturePaths.specular);
    const cloudsTexture = await textureLoader.loadAsync(texturePaths.clouds);

    // Configurar materiales
    earthTexture.anisotropy = renderer.capabilities.getMaxAnisotropy();
    bumpMap.anisotropy = renderer.capabilities.getMaxAnisotropy();
    specularMap.anisotropy = renderer.capabilities.getMaxAnisotropy();
    cloudsTexture.anisotropy = renderer.capabilities.getMaxAnisotropy();

    // Material para la Tierra
    const earthMaterial = new THREE.MeshPhongMaterial({
      map: earthTexture,
      bumpMap: bumpMap,
      bumpScale: 0.05,
      specularMap: specularMap,
      specular: new THREE.Color(0x333333),
      shininess: 25, // Más brillo
      emissive: new THREE.Color(0x0a0e29), // Color base para zonas oscuras
      emissiveIntensity: 0.1,
    });

    const earthGeometry = new THREE.SphereGeometry(1, 128, 128);
    earth = new THREE.Mesh(earthGeometry, earthMaterial);
    scene.add(earth);

    // Material para las nubes
    const cloudsMaterial = new THREE.MeshPhongMaterial({
      map: cloudsTexture,
      transparent: true,
      opacity: 0.9, // Más visibles
      depthWrite: false,
      emissive: 0xffffff,
      emissiveIntensity: 0.1,
    });

    const cloudsGeometry = new THREE.SphereGeometry(1.005, 128, 128);
    const clouds = new THREE.Mesh(cloudsGeometry, cloudsMaterial);
    scene.add(clouds);

    // Crear atmósfera
    createAtmosphere();
  } catch (err) {
    console.error("Error loading Earth textures:", err);
    // Fallback a texturas básicas con mejor apariencia
    createBasicEarth();
  }
}

function createAtmosphere() {
  const atmosphereGeometry = new THREE.SphereGeometry(1.02, 128, 128);
  const atmosphereMaterial = new THREE.MeshPhongMaterial({
    color: 0x5588dd,
    transparent: true,
    opacity: 0.25, // Más visible
    side: THREE.BackSide,
    shininess: 0,
  });

  const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
  scene.add(atmosphere);

  // Efecto de halo atmosférico
  const haloGeometry = new THREE.RingGeometry(1.05, 1.15, 64);
  const haloMaterial = new THREE.MeshBasicMaterial({
    color: 0x00aaff,
    transparent: true,
    opacity: 0.2,
    side: THREE.DoubleSide,
  });

  const halo = new THREE.Mesh(haloGeometry, haloMaterial);
  halo.rotation.x = Math.PI / 2;
  scene.add(halo);
}

function createBasicEarth() {
  // Crear texturas básicas como fallback con mejor apariencia
  const earthTexture = createFallbackTexture("#1a5c9e", "#0a4a36", "#d8d0c1");
  const bumpMap = createGradientTexture();
  const specularMap = createGradientTexture();

  const geometry = new THREE.SphereGeometry(1, 64, 64);
  const material = new THREE.MeshPhongMaterial({
    map: earthTexture,
    bumpMap: bumpMap,
    bumpScale: 0.08, // Más relieve
    specularMap: specularMap,
    specular: new THREE.Color(0x555555), // Más especular
    shininess: 15,
    emissive: 0x0a0e29,
    emissiveIntensity: 0.1,
  });

  earth = new THREE.Mesh(geometry, material);
  scene.add(earth);

  // Nubes básicas con mejor apariencia
  const cloudsMaterial = new THREE.MeshPhongMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 0.3,
    emissive: 0xffffff,
    emissiveIntensity: 0.05,
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

  // Crear geometría de satélite (más grande)
  const geometry = new THREE.SphereGeometry(0.025, 12, 12); // Tamaño aumentado

  satellites.value.forEach((sat, index) => {
    // Generar posición corregida
    const position = generateSatellitePosition(sat, index);

    // Color diferente para satélites de demostración
    const isDemo = sat.id.includes("demo");
    const color = isDemo ? 0xff7700 : 0xffff00;

    const material = new THREE.MeshPhongMaterial({
      color: color,
      emissive: color,
      emissiveIntensity: 1.0, // Más brillo
      shininess: 100,
    });

    const satellite = new THREE.Mesh(geometry, material);
    satellite.position.copy(position);

    // Orientar el satélite hacia la Tierra
    satellite.lookAt(new THREE.Vector3(0, 0, 0));

    // Agregar efecto de halo
    const haloGeometry = new THREE.SphereGeometry(0.035, 8, 8);
    const haloMaterial = new THREE.MeshBasicMaterial({
      color: color,
      transparent: true,
      opacity: 0.3,
      side: THREE.BackSide,
    });

    const halo = new THREE.Mesh(haloGeometry, haloMaterial);
    satellite.add(halo);

    // Guardar datos para filtrado
    satellite.userData = {
      inclination: sat.inclination_deg,
      altitude: sat.altitude_km || 550,
      isDemo: isDemo,
    };

    satelliteGroup.add(satellite);
    satObjects.push(satellite);
  });
}

function generateSatellitePosition(
  sat: StarlinkSatellite,
  index: number
): THREE.Vector3 {
  const inclination = sat.inclination_deg;
  const altitude = sat.altitude_km || 550;
  const orbitRadius = 1 + altitude / 6371;
  const orbitAngle = (index / satellites.value.length) * Math.PI * 2;

  // Cálculo de posición corregido
  const inclinationRad = (inclination * Math.PI) / 180;

  return new THREE.Vector3(
    orbitRadius * Math.cos(orbitAngle) * Math.cos(inclinationRad),
    orbitRadius * Math.sin(inclinationRad),
    orbitRadius * Math.sin(orbitAngle) * Math.cos(inclinationRad)
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

  // Rotar satélites alrededor de la Tierra
  satelliteGroup.rotation.y += 0.001;

  // Animación de satélites
  satObjects.forEach((sat, index) => {
    // Efecto de "parpadeo" para satélites de demostración
    if (sat.userData.isDemo) {
      const blink = Math.sin(Date.now() * 0.005 + index) * 0.5 + 0.5;
      (sat.material as THREE.MeshPhongMaterial).emissiveIntensity = blink * 1.2;
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

// Funciones para generar texturas de fallback
function createFallbackTexture(
  color1: string,
  color2: string,
  color3: string
): THREE.Texture {
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext("2d")!;

  // Crear un mapa de la Tierra simple
  ctx.fillStyle = color1; // Océanos
  ctx.fillRect(0, 0, 512, 512);

  // Continentes con más detalle
  ctx.fillStyle = color2;

  // América del Norte
  ctx.beginPath();
  ctx.moveTo(100, 150);
  ctx.bezierCurveTo(120, 100, 150, 120, 180, 180);
  ctx.bezierCurveTo(150, 220, 100, 250, 80, 200);
  ctx.closePath();
  ctx.fill();

  // América del Sur
  ctx.beginPath();
  ctx.moveTo(150, 250);
  ctx.bezierCurveTo(170, 300, 140, 350, 100, 380);
  ctx.bezierCurveTo(80, 350, 90, 300, 120, 270);
  ctx.closePath();
  ctx.fill();

  // Europa/Asia
  ctx.fillStyle = color3;
  ctx.beginPath();
  ctx.moveTo(300, 150);
  ctx.bezierCurveTo(350, 130, 380, 180, 370, 220);
  ctx.bezierCurveTo(340, 250, 310, 280, 280, 250);
  ctx.bezierCurveTo(270, 200, 280, 170, 300, 150);
  ctx.closePath();
  ctx.fill();

  // África
  ctx.beginPath();
  ctx.moveTo(280, 220);
  ctx.bezierCurveTo(300, 250, 290, 300, 260, 330);
  ctx.bezierCurveTo(230, 320, 220, 280, 240, 250);
  ctx.closePath();
  ctx.fill();

  // Australia
  ctx.beginPath();
  ctx.moveTo(420, 320);
  ctx.bezierCurveTo(440, 300, 460, 320, 450, 350);
  ctx.bezierCurveTo(430, 370, 410, 360, 410, 340);
  ctx.closePath();
  ctx.fill();

  return new THREE.CanvasTexture(canvas);
}

function createGradientTexture(): THREE.Texture {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext("2d")!;

  const gradient = ctx.createRadialGradient(128, 128, 0, 128, 128, 128);
  gradient.addColorStop(0, "#000000");
  gradient.addColorStop(0.7, "#444444");
  gradient.addColorStop(1, "#888888");

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
  background: radial-gradient(ellipse at center, #0a0e29 0%, #00040f 80%);
  color: #d5faff;
  padding: 20px;
  min-height: 100vh;
  font-family: "Orbitron", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  position: relative;
}

.glow-title {
  text-align: center;
  font-size: 3rem;
  margin-bottom: 30px;
  text-shadow: 0 0 15px #00fff7, 0 0 30px #00d1ff;
  letter-spacing: 3px;
  text-transform: uppercase;
}

.globe-container {
  width: 100%;
  height: 80vh;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 0 40px rgba(0, 255, 255, 0.3);
  background: #000814;
}

.globe-container canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.orbit-controls {
  background: rgba(10, 15, 40, 0.8);
  border: 1px solid rgba(0, 255, 255, 0.5);
  border-radius: 16px;
  padding: 20px;
  margin: 0 auto 30px;
  backdrop-filter: blur(10px);
  max-width: 850px;
  transition: box-shadow 0.3s ease;
  box-shadow: 0 0 25px rgba(0, 255, 255, 0.3);
  z-index: 10;
  position: relative;
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
  color: #00fff7;
  text-transform: uppercase;
  text-shadow: 0 0 8px rgba(0, 255, 255, 0.6);
}

.toggle-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.toggle-group button {
  flex: 1;
  min-width: 160px;
  padding: 12px 15px;
  border-radius: 10px;
  border: 1px solid rgba(0, 255, 255, 0.4);
  background: rgba(0, 20, 40, 0.6);
  color: #b0f0ff;
  cursor: pointer;
  font-weight: 600;
  letter-spacing: 1px;
  transition: all 0.25s ease;
  text-transform: uppercase;
  font-size: 0.9rem;
}

.toggle-group button:hover {
  background: rgba(0, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 0 15px rgba(0, 255, 255, 0.4);
}

.toggle-group button.active {
  background: linear-gradient(
    45deg,
    rgba(0, 255, 255, 0.3),
    rgba(157, 78, 221, 0.3)
  );
  border-color: #00fff7;
  box-shadow: 0 0 25px rgba(0, 255, 255, 0.6);
  color: #ffffff;
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
  padding: 10px 20px;
  border-radius: 20px;
  background: rgba(0, 10, 30, 0.6);
  border: 1px solid rgba(0, 255, 255, 0.4);
  box-shadow: 0 0 15px rgba(0, 255, 255, 0.2);
  font-size: 1rem;
  font-weight: 500;
}

.sat-icon {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #00fff7;
  box-shadow: 0 0 10px #00fff7;
}

/* CARGA */
.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  gap: 15px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
  background: rgba(10, 15, 40, 0.8);
  border-radius: 16px;
  border: 1px solid rgba(0, 255, 255, 0.3);
  backdrop-filter: blur(10px);
}

.spinner {
  width: 60px;
  height: 60px;
  border: 5px solid rgba(0, 255, 255, 0.2);
  border-top: 5px solid #00fff7;
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* ERROR */
.error-toast {
  background: rgba(255, 40, 40, 0.2);
  border: 1px solid rgba(255, 80, 80, 0.4);
  border-radius: 10px;
  padding: 12px 20px;
  margin: 15px auto;
  max-width: 500px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(10px);
  box-shadow: 0 0 20px rgba(255, 0, 0, 0.3);
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
}

.error-toast button {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 1.2rem;
  margin-left: 15px;
}

/* TRANSICIONES */
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

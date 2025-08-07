<template>
  <div ref="globeContainer" class="globe-container"></div>
</template>

<script setup lang="ts">
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { onMounted, onUnmounted, ref, watch, nextTick } from "vue";

interface StarlinkSatellite {
  id: string;
  name: string;
  latitude: number | null;
  longitude: number | null;
  altitude_km: number | null;
  inclination_deg: number;
}

const props = defineProps<{
  satellites: StarlinkSatellite[];
  highlightOrbit?: "polar" | "geostationary" | null;
}>();

const globeContainer = ref<HTMLElement | null>(null);

// Escena Three.js
let scene: THREE.Scene;
let camera: THREE.PerspectiveCamera;
let renderer: THREE.WebGLRenderer;
let controls: OrbitControls;
let earth: THREE.Mesh;
let satelliteGroup: THREE.Group;
const satObjects: THREE.Mesh[] = [];

onMounted(() => {
  nextTick(() => {
    initGlobe();
  });
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
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5)); // Optimizar para rendimiento
  globeContainer.value.appendChild(renderer.domElement);

  // 4. Controles de órbita
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.rotateSpeed = 0.5;
  controls.enablePan = false;
  controls.enableZoom = true;
  controls.screenSpacePanning = false;
  controls.mouseButtons = {
    LEFT: THREE.MOUSE.ROTATE,
    MIDDLE: THREE.MOUSE.DOLLY,
    RIGHT: THREE.MOUSE.ROTATE,
  };

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

    // Rutas CORREGIDAS (sin / inicial)
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
      shininess: 15,
    });

    const earthGeometry = new THREE.SphereGeometry(1, 64, 64); // Reducir geometría para rendimiento
    earth = new THREE.Mesh(earthGeometry, earthMaterial);
    scene.add(earth);

    // Material para las nubes
    const cloudsMaterial = new THREE.MeshPhongMaterial({
      map: cloudsTexture,
      transparent: true,
      opacity: 0.8,
      depthWrite: false,
    });

    const cloudsGeometry = new THREE.SphereGeometry(1.005, 64, 64); // Reducir geometría
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
  const atmosphereGeometry = new THREE.SphereGeometry(1.02, 32, 32); // Reducir geometría
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
  const geometry = new THREE.SphereGeometry(0.015, 6, 6); // Geometría más simple

  props.satellites.forEach((sat, index) => {
    let position: THREE.Vector3;
    const isDemo = sat.id.includes("demo");

    if (sat.inclination_deg <= 5) {
      // Satélites geoestacionarios
      const orbitAngle = (index / props.satellites.length) * Math.PI * 2;
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
  const orbitAngle = (index / props.satellites.length) * Math.PI * 2;

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

    if (!props.highlightOrbit) {
      visible = true;
    } else if (props.highlightOrbit === "polar") {
      visible = sat.userData.inclination >= 85;
    } else if (props.highlightOrbit === "geostationary") {
      visible = sat.userData.inclination <= 5;
    }

    // Mantener visibles los satélites de demostración en sus categorías
    if (sat.userData.isDemo) {
      if (props.highlightOrbit === "polar" && sat.userData.inclination >= 85) {
        visible = true;
      } else if (
        props.highlightOrbit === "geostationary" &&
        sat.userData.inclination <= 5
      ) {
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

watch(
  () => props.highlightOrbit,
  () => {
    updateSatelliteVisibility();
  }
);
</script>

<style scoped>
.globe-container {
  width: 100%;
  height: 100%;
  border-radius: 16px;
  overflow: hidden;
}
</style>

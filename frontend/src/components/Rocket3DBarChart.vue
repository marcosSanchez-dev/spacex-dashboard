<template>
  <div class="rocket-3d-chart">
    <div ref="chartContainer" class="chart-canvas"></div>
    <div class="chart-legend">
      <div class="legend-item">
        <div class="color-box height"></div>
        <span>Height (meters)</span>
      </div>
      <div class="legend-item">
        <div class="color-box mass"></div>
        <span>Mass (kg)</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { ref, onMounted, onUnmounted, watch } from "vue";

interface RocketData {
  id: string;
  name: string;
  height: number | { meters: number };
  mass: number | { kg: number };
  first_flight?: string;
  success_rate?: number;
}

const props = defineProps({
  data: {
    type: Array as () => RocketData[],
    required: true,
    default: () => [],
  },
  year: Number,
});

const chartContainer = ref<HTMLElement | null>(null);
let scene: THREE.Scene;
let camera: THREE.PerspectiveCamera;
let renderer: THREE.WebGLRenderer;
let controls: OrbitControls;
let bars: THREE.Mesh[] = [];
let labels: THREE.Sprite[] = []; // Almacenar etiquetas para poder eliminarlas
const barSpacing = 4;
const maxBarHeight = 20;

onMounted(() => {
  if (!chartContainer.value) return;
  initThreeJS();
  createScene();
  animate();
});

onUnmounted(() => {
  if (renderer) renderer.dispose();
  window.removeEventListener("resize", onWindowResize); // Limpiar evento
});

watch(
  () => props.data,
  (newData) => {
    if (newData && newData.length > 0) {
      updateChart();
    }
  },
  { deep: true }
);

watch(
  () => props.year,
  () => {
    updateChart();
  }
);

function initThreeJS() {
  if (!chartContainer.value) return;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x000814);
  scene.fog = new THREE.Fog(0x000814, 20, 60);

  camera = new THREE.PerspectiveCamera(
    45, // Ángulo de visión más amplio
    chartContainer.value.clientWidth / chartContainer.value.clientHeight,
    0.1,
    1000
  );
  // Posición de cámara ajustada para mejor visualización
  camera.position.set(10, 15, 30);

  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    logarithmicDepthBuffer: true, // Mejorar profundidad
  });
  renderer.setSize(
    chartContainer.value.clientWidth,
    chartContainer.value.clientHeight
  );
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  chartContainer.value.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.rotateSpeed = 0.5;
  controls.minDistance = 15;
  controls.maxDistance = 50;

  // Mejor iluminación
  scene.add(new THREE.AmbientLight(0xffffff, 1.5)); // Intensidad aumentada
  const dirLight = new THREE.DirectionalLight(0x00fff7, 2.0); // Más brillante
  dirLight.position.set(5, 20, 15);
  scene.add(dirLight);

  const fillLight = new THREE.DirectionalLight(0xffffff, 0.8);
  fillLight.position.set(-10, 5, -10);
  scene.add(fillLight);

  // Grid más visible
  const gridHelper = new THREE.GridHelper(50, 10, 0x00c3ff, 0x004d66);
  (gridHelper.material as THREE.Material).opacity = 0.4;
  (gridHelper.material as THREE.Material).transparent = true;
  scene.add(gridHelper);

  // Ejes de referencia
  const axesHelper = new THREE.AxesHelper(10);
  scene.add(axesHelper);

  window.addEventListener("resize", onWindowResize);
}

function createScene() {
  // Limpiar barras y etiquetas existentes
  bars.forEach((bar) => scene.remove(bar));
  labels.forEach((label) => scene.remove(label));
  bars = [];
  labels = [];

  if (!props.data || props.data.length === 0) return;

  props.data.forEach((rocket: RocketData, index) => {
    const x = index * barSpacing - ((props.data.length - 1) * barSpacing) / 2;

    // Manejar diferentes formatos de altura
    const heightValue =
      typeof rocket.height === "object" ? rocket.height.meters : rocket.height;

    // Manejar diferentes formatos de masa
    const massValue =
      typeof rocket.mass === "object" ? rocket.mass.kg : rocket.mass;

    // Escalas ajustadas para mejor visualización
    const heightScale = Math.min(heightValue / 70, 1);
    const massScale = Math.min(massValue / 1400000, 1);

    const heightBar = createBar(
      heightScale * maxBarHeight,
      1.5,
      1.5,
      0x00fff7,
      { x, y: (heightScale * maxBarHeight) / 2, z: -1.5 },
      rocket.name,
      `${heightValue.toLocaleString()}m`
    );

    const massBar = createBar(
      massScale * maxBarHeight,
      1.5,
      1.5,
      0x00c3ff,
      { x, y: (massScale * maxBarHeight) / 2, z: 1.5 },
      rocket.name,
      `${massValue.toLocaleString()}kg`
    );

    scene.add(heightBar, massBar);
    bars.push(heightBar, massBar);

    // Etiquetas más visibles
    const label = createTextLabel(rocket.name, new THREE.Vector3(x, -2.5, 0));
    scene.add(label);
    labels.push(label); // Guardar referencia a la etiqueta
  });
}

function createBar(
  height: number,
  width: number,
  depth: number,
  color: number,
  position: { x: number; y: number; z: number },
  rocketName: string,
  value: string
) {
  const geometry = new THREE.BoxGeometry(width, height, depth);
  const material = new THREE.MeshPhongMaterial({
    color,
    emissive: color,
    emissiveIntensity: 0.5, // Aumentado para más brillo
    shininess: 100,
    specular: 0xffffff,
  });

  const bar = new THREE.Mesh(geometry, material);
  bar.position.set(position.x, position.y, position.z);

  // Bordes brillantes
  const edges = new THREE.EdgesGeometry(geometry);
  const line = new THREE.LineSegments(
    edges,
    new THREE.LineBasicMaterial({
      color: 0xffffff,
      linewidth: 2,
      transparent: true,
      opacity: 0.8, // Más visible
    })
  );
  bar.add(line);

  bar.userData = { rocketName, value };
  return bar;
}

function createTextLabel(text: string, position: THREE.Vector3) {
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d")!;
  canvas.width = 256;
  canvas.height = 64;

  // Fondo más transparente
  context.fillStyle = "rgba(10, 14, 41, 0.7)";
  context.fillRect(0, 0, canvas.width, canvas.height);

  context.font = "bold 22px Orbitron, Arial";
  context.fillStyle = "#00fff7";
  context.textAlign = "center";
  context.textBaseline = "middle";
  context.shadowColor = "#00c3ff";
  context.shadowBlur = 10; // Más brillo
  context.fillText(text, canvas.width / 2, canvas.height / 2);

  const texture = new THREE.CanvasTexture(canvas);
  const material = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
  });
  const sprite = new THREE.Sprite(material);
  sprite.position.copy(position);
  sprite.scale.set(10, 2.5, 1); // Más grande
  return sprite;
}

function updateChart() {
  createScene();
}

function onWindowResize() {
  if (!chartContainer.value) return;

  camera.aspect =
    chartContainer.value.clientWidth / chartContainer.value.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(
    chartContainer.value.clientWidth,
    chartContainer.value.clientHeight
  );
}

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
</script>

<style scoped>
.rocket-3d-chart {
  position: relative;
  width: 100%;
  height: 100%;
}

.chart-canvas {
  width: 100%;
  height: 100%;
}

.chart-legend {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(10, 14, 41, 0.8);
  border: 1px solid rgba(0, 255, 255, 0.5);
  border-radius: 10px;
  padding: 12px 18px;
  backdrop-filter: blur(10px);
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.4);
  z-index: 10;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 8px 0;
  color: #d0faff;
  font-family: "Orbitron", sans-serif;
  font-size: 1rem;
  font-weight: 500;
}

.color-box {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  box-shadow: 0 0 12px;
}

.color-box.height {
  background: #00fff7;
  box-shadow: 0 0 12px #00fff7;
}

.color-box.mass {
  background: #00c3ff;
  box-shadow: 0 0 12px #00c3ff;
}
</style>

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
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import { ref, onMounted, onUnmounted, watch } from "vue";

// Definir interfaz para los datos del cohete
interface RocketData {
  name: string;
  height: number;
  mass: number;
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
const barSpacing = 4;
const maxBarHeight = 20;

onMounted(() => {
  if (!chartContainer.value) return;

  initThreeJS();
  createScene();
  animate();
});

onUnmounted(() => {
  if (renderer) {
    renderer.dispose();
  }
});

watch(
  () => props.data,
  (newData) => {
    if (newData && newData.length > 0) {
      updateChart();
    }
  }
);

watch(
  () => props.year,
  () => {
    updateChart();
  }
);

function initThreeJS() {
  // Escena
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a0e29);
  scene.fog = new THREE.Fog(0x0a0e29, 20, 50);

  // Cámara
  camera = new THREE.PerspectiveCamera(
    75,
    chartContainer.value!.clientWidth / chartContainer.value!.clientHeight,
    0.1,
    1000
  );
  camera.position.set(0, 10, 30);

  // Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(
    chartContainer.value!.clientWidth,
    chartContainer.value!.clientHeight
  );
  renderer.setPixelRatio(window.devicePixelRatio);
  chartContainer.value!.appendChild(renderer.domElement);

  // Controles
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.rotateSpeed = 0.5;
  controls.minDistance = 15;
  controls.maxDistance = 50;

  // Luz ambiental
  const ambientLight = new THREE.AmbientLight(0x404040, 2);
  scene.add(ambientLight);

  // Luz direccional
  const directionalLight = new THREE.DirectionalLight(0x00ffff, 1);
  directionalLight.position.set(0, 10, 10);
  scene.add(directionalLight);

  // Luz de relleno
  const fillLight = new THREE.DirectionalLight(0x9d4edd, 0.5);
  fillLight.position.set(-10, 5, -10);
  scene.add(fillLight);

  // Ejes de referencia
  const axesHelper = new THREE.AxesHelper(20);
  scene.add(axesHelper);

  // Suelo
  const gridHelper = new THREE.GridHelper(50, 10, 0x00ffff, 0x008888);
  (gridHelper.material as THREE.Material).opacity = 0.2;
  (gridHelper.material as THREE.Material).transparent = true;
  scene.add(gridHelper);

  window.addEventListener("resize", onWindowResize);
}

function createScene() {
  // Limpiar barras existentes
  bars.forEach((bar) => scene.remove(bar));
  bars = [];

  // Verificar que data existe y tiene elementos
  if (!props.data || props.data.length === 0) return;

  // Crear barras para cada cohete con tipo explícito
  props.data.forEach((rocket: RocketData, index) => {
    const x = index * barSpacing - ((props.data.length - 1) * barSpacing) / 2;

    // Barra de altura
    const heightScale = rocket.height / 70;
    const heightBar = createBar(
      heightScale * maxBarHeight,
      1.5,
      1.5,
      0x00ff9d,
      { x, y: (heightScale * maxBarHeight) / 2, z: -1.5 },
      rocket.name,
      `${rocket.height.toLocaleString()}m`
    );

    // Barra de masa
    const massScale = rocket.mass / 1400000;
    const massBar = createBar(
      massScale * maxBarHeight,
      1.5,
      1.5,
      0x9d4edd,
      { x, y: (massScale * maxBarHeight) / 2, z: 1.5 },
      rocket.name,
      `${rocket.mass.toLocaleString()}kg`
    );

    scene.add(heightBar);
    scene.add(massBar);
    bars.push(heightBar, massBar);

    // Etiqueta del cohete
    const label = createTextLabel(rocket.name, new THREE.Vector3(x, -1, 0));
    scene.add(label);
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

  // Material con efecto de borde brillante
  const material = new THREE.MeshPhongMaterial({
    color: color,
    emissive: color,
    emissiveIntensity: 0.1,
    shininess: 100,
    specular: 0xffffff,
  });

  const bar = new THREE.Mesh(geometry, material);
  bar.position.set(position.x, position.y, position.z);

  // Agregar efecto de brillo
  const edges = new THREE.EdgesGeometry(geometry);
  const line = new THREE.LineSegments(
    edges,
    new THREE.LineBasicMaterial({
      color: 0xffffff,
      linewidth: 2,
      transparent: true,
      opacity: 0.7,
    })
  );
  bar.add(line);

  // Tooltip interactivo
  bar.userData = { rocketName, value };

  return bar;
}

function createTextLabel(text: string, position: THREE.Vector3) {
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d")!;
  canvas.width = 256;
  canvas.height = 64;

  context.fillStyle = "#0a0e29";
  context.fillRect(0, 0, canvas.width, canvas.height);

  context.font = "24px Arial";
  context.fillStyle = "#80deea";
  context.textAlign = "center";
  context.fillText(text, canvas.width / 2, 40);

  const texture = new THREE.CanvasTexture(canvas);
  const material = new THREE.SpriteMaterial({ map: texture });
  const sprite = new THREE.Sprite(material);
  sprite.position.copy(position);
  sprite.scale.set(8, 2, 1);

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

  // Rotación suave de la escena
  scene.rotation.y += 0.001;

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
  background: rgba(10, 14, 41, 0.7);
  border: 1px solid rgba(0, 231, 255, 0.3);
  border-radius: 8px;
  padding: 10px 15px;
  backdrop-filter: blur(5px);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 5px 0;
}

.color-box {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.color-box.height {
  background: #00ff9d;
  box-shadow: 0 0 8px #00ff9d;
}

.color-box.mass {
  background: #9d4edd;
  box-shadow: 0 0 8px #9d4edd;
}
</style>

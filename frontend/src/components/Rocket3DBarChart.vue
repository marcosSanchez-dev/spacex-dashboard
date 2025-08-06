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
  if (renderer) renderer.dispose();
});

watch(
  () => props.data,
  () => {
    updateChart();
  }
);

watch(
  () => props.year,
  () => {
    updateChart();
  }
);

function initThreeJS() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x000814);
  scene.fog = new THREE.Fog(0x000814, 20, 60);

  camera = new THREE.PerspectiveCamera(
    75,
    chartContainer.value!.clientWidth / chartContainer.value!.clientHeight,
    0.1,
    1000
  );
  camera.position.set(0, 10, 30);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(
    chartContainer.value!.clientWidth,
    chartContainer.value!.clientHeight
  );
  renderer.setPixelRatio(window.devicePixelRatio);
  chartContainer.value!.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.rotateSpeed = 0.5;
  controls.minDistance = 15;
  controls.maxDistance = 50;

  scene.add(new THREE.AmbientLight(0x222222, 2));
  const dirLight = new THREE.DirectionalLight(0x00fff7, 1.2);
  dirLight.position.set(0, 10, 10);
  scene.add(dirLight);

  const fillLight = new THREE.DirectionalLight(0xffffff, 0.5);
  fillLight.position.set(-10, 5, -10);
  scene.add(fillLight);

  const gridHelper = new THREE.GridHelper(50, 10, 0x00c3ff, 0x004d66);
  (gridHelper.material as THREE.Material).opacity = 0.2;
  (gridHelper.material as THREE.Material).transparent = true;
  scene.add(gridHelper);

  window.addEventListener("resize", onWindowResize);
}

function createScene() {
  bars.forEach((bar) => scene.remove(bar));
  bars = [];

  if (!props.data || props.data.length === 0) return;

  props.data.forEach((rocket: RocketData, index) => {
    const x = index * barSpacing - ((props.data.length - 1) * barSpacing) / 2;

    const heightScale = rocket.height / 70;
    const heightBar = createBar(
      heightScale * maxBarHeight,
      1.5,
      1.5,
      0x00fff7,
      { x, y: (heightScale * maxBarHeight) / 2, z: -1.5 },
      rocket.name,
      `${rocket.height.toLocaleString()}m`
    );

    const massScale = rocket.mass / 1400000;
    const massBar = createBar(
      massScale * maxBarHeight,
      1.5,
      1.5,
      0x00c3ff,
      { x, y: (massScale * maxBarHeight) / 2, z: 1.5 },
      rocket.name,
      `${rocket.mass.toLocaleString()}kg`
    );

    scene.add(heightBar, massBar);
    bars.push(heightBar, massBar);

    const label = createTextLabel(rocket.name, new THREE.Vector3(x, -1.5, 0));
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
  const material = new THREE.MeshPhongMaterial({
    color,
    emissive: color,
    emissiveIntensity: 0.2,
    shininess: 100,
    specular: 0xffffff,
  });

  const bar = new THREE.Mesh(geometry, material);
  bar.position.set(position.x, position.y, position.z);

  const edges = new THREE.EdgesGeometry(geometry);
  const line = new THREE.LineSegments(
    edges,
    new THREE.LineBasicMaterial({
      color: 0xffffff,
      linewidth: 2,
      transparent: true,
      opacity: 0.6,
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

  context.fillStyle = "#000814";
  context.fillRect(0, 0, canvas.width, canvas.height);

  context.font = "24px Orbitron, Arial";
  context.fillStyle = "#00fff7";
  context.textAlign = "center";
  context.shadowColor = "#00c3ff";
  context.shadowBlur = 8;
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
  background: rgba(10, 14, 41, 0.6);
  border: 1px solid rgba(0, 255, 255, 0.3);
  border-radius: 10px;
  padding: 10px 15px;
  backdrop-filter: blur(6px);
  box-shadow: 0 0 12px rgba(0, 255, 255, 0.2);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 6px 0;
  color: #d0faff;
  font-family: "Orbitron", sans-serif;
  font-size: 0.9rem;
}

.color-box {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  box-shadow: 0 0 8px;
}

.color-box.height {
  background: #00fff7;
  box-shadow: 0 0 8px #00fff7;
}

.color-box.mass {
  background: #00c3ff;
  box-shadow: 0 0 8px #00c3ff;
}
</style>

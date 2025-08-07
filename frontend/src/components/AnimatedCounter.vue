<template>
  <div class="animated-number" :class="{ pulse: pulseActive }">
    {{ displayedValue }}
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";

const props = defineProps<{
  target: number;
  duration?: number;
}>();

const displayedValue = ref(0);
const pulseActive = ref(false);

const animate = () => {
  const start = 0;
  const end = props.target;
  const duration = props.duration || 1000;
  const startTime = performance.now();
  pulseActive.value = false;

  const tick = (now: number) => {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    displayedValue.value = Math.floor(start + (end - start) * progress);
    if (progress < 1) {
      requestAnimationFrame(tick);
    } else {
      pulseActive.value = true;
    }
  };

  requestAnimationFrame(tick);
};

onMounted(animate);
watch(() => props.target, animate);
</script>

<style scoped>
.animated-number {
  font-size: 2.8rem;
  text-align: center;
  font-weight: bold;
  font-family: "Orbitron", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  color: #00e6ff;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.6), 0 0 20px rgba(0, 255, 255, 0.3);
  transition: transform 0.3s ease, text-shadow 0.3s ease;
}

/* Efecto pulso al llegar al final */
.pulse {
  animation: pulseGlow 0.8s ease;
}

@keyframes pulseGlow {
  0% {
    transform: scale(1);
    text-shadow: 0 0 8px rgba(0, 255, 255, 0.4);
  }
  50% {
    transform: scale(1.1);
    text-shadow: 0 0 20px rgba(0, 255, 255, 0.8);
  }
  100% {
    transform: scale(1);
    text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
  }
}
</style>

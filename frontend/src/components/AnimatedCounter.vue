<template>
  <div class="glow-box big-number">{{ displayedValue }}</div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";

const props = defineProps<{
  target: number;
  duration?: number;
}>();

const displayedValue = ref(0);

const animate = () => {
  const start = 0;
  const end = props.target;
  const duration = props.duration || 1000;
  const startTime = performance.now();

  const tick = (now: number) => {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    displayedValue.value = Math.floor(start + (end - start) * progress);
    if (progress < 1) {
      requestAnimationFrame(tick);
    }
  };

  requestAnimationFrame(tick);
};

onMounted(animate);
watch(() => props.target, animate);
</script>

<style scoped>
.big-number {
  font-size: 48px;
  text-align: center;
}
</style>

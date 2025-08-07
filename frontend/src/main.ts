// src/main.ts
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { createPinia } from "pinia";
import "./assets/styles/glow.css";
import "./assets/styles/global.css"; // ← nuevo: estilos globales con fuente y variables

// Cargar fuente 'Orbitron' desde Google Fonts (solo si no la estás cargando en index.html)
const orbitronFont = new FontFace(
  "Orbitron",
  "url(https://fonts.gstatic.com/s/orbitron/v28/yMJRMIlzdpvBhQQL_Qq7dys.woff2)"
);
orbitronFont.load().then(() => {
  document.fonts.add(orbitronFont);
  document.body.style.fontFamily = '"Orbitron", sans-serif';
});

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount("#app");

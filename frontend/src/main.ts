// src/main.ts
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { createPinia } from "pinia";
import "./assets/styles/glow.css";
import "./assets/styles/global.css"; // ← nuevo: estilos globales con fuente y variables

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount("#app");

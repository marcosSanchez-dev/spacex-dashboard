import { createRouter, createWebHistory } from "vue-router";
import DashboardView from "../views/DashboardView.vue";
import RocketsView from "../views/RocketsView.vue";
import StarlinkView from "../views/StarlinkView.vue";

const routes = [
  { path: "/", name: "Dashboard", component: DashboardView },
  { path: "/rockets", name: "Rockets", component: RocketsView },
  { path: "/starlink", name: "Starlink", component: StarlinkView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

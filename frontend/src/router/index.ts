import { createRouter, createWebHistory } from "vue-router"

import { getToken } from "../auth/session"

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: () => (getToken() ? "/app/dashboard" : "/login") },
    { path: "/login", component: () => import("../views/LoginView.vue") },
    { path: "/register", component: () => import("../views/RegisterView.vue") },
    {
      path: "/app",
      component: () => import("../views/AppShell.vue"),
      children: [
        { path: "", redirect: "/app/dashboard" },
        { path: "dashboard", component: () => import("../views/DashboardView.vue") },
        { path: "pets", component: () => import("../views/PetsView.vue") },
        { path: "pets/:id", component: () => import("../views/PetView.vue") },
        { path: "owners", component: () => import("../views/OwnersView.vue") },
        { path: "owners/:id", component: () => import("../views/OwnerView.vue") },
        { path: "visits", component: () => import("../views/VisitsView.vue") },
        { path: "visits/new", component: () => import("../views/VisitFormView.vue") },
        { path: "visits/:id", component: () => import("../views/VisitDetailView.vue") },
        { path: "services", component: () => import("../views/ServicesView.vue") },
        { path: "vaccinations", component: () => import("../views/VaccinationsView.vue") },
        { path: "analytics", component: () => import("../views/AnalyticsView.vue") },
        { path: "settings", component: () => import("../views/SettingsView.vue") },
      ],
    },
    { path: "/:pathMatch(.*)*", redirect: () => (getToken() ? "/app/dashboard" : "/login") },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  const authed = Boolean(getToken())
  if (to.path.startsWith("/app") && !authed) return "/login"
  if ((to.path === "/login" || to.path === "/register") && authed) return "/app/dashboard"
  return true
})

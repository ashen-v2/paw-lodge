import { createApp } from "vue"
import { VueQueryPlugin } from "@tanstack/vue-query"

import { setUnauthorizedHandler } from "./api/client"
import { clearToken } from "./auth/session"
import { queryClient } from "./query"
import { router } from "./router"
import App from "./App.vue"
import "./style.css"

setUnauthorizedHandler(() => {
  clearToken()
  queryClient.clear()
  if (router.currentRoute.value.path !== "/login") {
    void router.replace({ path: "/login", query: { expired: "1" } })
  }
})

createApp(App).use(router).use(VueQueryPlugin, { queryClient }).mount("#app")

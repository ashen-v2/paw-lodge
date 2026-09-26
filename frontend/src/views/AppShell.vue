<script setup lang="ts">
import { computed, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useQueryClient } from "@tanstack/vue-query"

import Drawer from "../components/Drawer.vue"
import NavIcon from "../components/NavIcon.vue"
import { clearToken } from "../auth/session"
import { roleLabel } from "../lib/dates"
import { presentQuery } from "../lib/present"
import { shell } from "../lib/shell"
import { usePractice } from "../queries/usePractice"
import { useMe } from "../queries/useSession"

const route = useRoute()
const router = useRouter()
const queryClient = useQueryClient()
const me = presentQuery(useMe())
const practice = presentQuery(usePractice())

const nav = [
  { to: "/app/dashboard", label: "Dashboard", icon: "home" },
  { to: "/app/pets", label: "Pets", icon: "paw" },
  { to: "/app/owners", label: "Owners", icon: "people" },
  { to: "/app/visits", label: "Visits", icon: "clipboard" },
  { to: "/app/services", label: "Services", icon: "tag" },
  { to: "/app/vaccinations", label: "Vaccinations", icon: "syringe" },
  { to: "/app/analytics", label: "Analytics", icon: "chart" },
  { to: "/app/settings", label: "Settings", icon: "gear" },
] as const

const bottom = [
  { to: "/app/dashboard", label: "Home", icon: "home" },
  { to: "/app/pets", label: "Pets", icon: "paw" },
  { to: "/app/visits", label: "Visits", icon: "clipboard" },
] as const

const moreLinks = nav.filter((item) => !["/app/dashboard", "/app/pets", "/app/visits"].includes(item.to))

function active(to: string): boolean {
  if (to === "/app/dashboard") return route.path === "/app/dashboard"
  return route.path === to || route.path.startsWith(`${to}/`)
}

const moreActive = computed(() => moreLinks.some((item) => active(item.to)))
const firstName = computed(() => me.data?.name.trim().split(/\s+/)[0] ?? "")

watch(
  () => route.fullPath,
  () => {
    shell.moreOpen = false
  },
)

watch(
  () => route.path,
  (path) => {
    const item = nav.find((entry) => active(entry.to))
    document.title = item ? `${item.label} · Paw Lodge` : path.startsWith("/app") ? "Paw Lodge" : "Paw Lodge"
  },
  { immediate: true },
)

function signOut() {
  clearToken()
  queryClient.clear()
  shell.moreOpen = false
  void router.push("/login")
}

function linkClass(to: string, emphasized = false): string {
  const on = active(to)
  return [
    "flex min-h-11 items-center gap-3 rounded-xl px-3 text-sm",
    emphasized ? "font-semibold" : "",
    on ? "bg-white/15 text-white" : "text-white/80 hover:bg-white/10",
    "focus-visible:outline-white",
  ].join(" ")
}
</script>

<template>
  <div class="min-h-dvh bg-paper text-ink">
    <a
      href="#main"
      class="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:rounded-lg focus:bg-card focus:px-3 focus:py-2"
    >
      Skip to content
    </a>

    <aside class="fixed inset-y-0 left-0 z-30 hidden w-60 flex-col bg-spruce text-white lg:flex">
      <div class="px-5 pb-4 pt-6">
        <p class="font-serif text-2xl">Paw Lodge</p>
        <p class="mt-1 truncate text-sm text-white/70">{{ practice.data?.name || "Clinic" }}</p>
      </div>
      <nav aria-label="Primary" class="flex-1 space-y-1 overflow-y-auto px-3">
        <RouterLink
          v-for="item in nav"
          :key="item.to"
          :to="item.to"
          :class="linkClass(item.to, item.to === '/app/pets')"
          :aria-current="active(item.to) ? 'page' : undefined"
        >
          <NavIcon :name="item.icon" />
          {{ item.label }}
        </RouterLink>
      </nav>
      <div class="border-t border-white/10 p-4">
        <p class="truncate text-sm font-medium">{{ me.data?.name || "Signed in" }}</p>
        <p class="truncate text-xs text-white/70">
          {{ me.data ? roleLabel(me.data.role) : "" }}
          <span v-if="me.data"> · {{ me.data.email }}</span>
        </p>
        <button
          type="button"
          class="mt-3 min-h-11 w-full rounded-xl px-3 text-left text-sm text-white/90 hover:bg-white/10 focus-visible:outline-white"
          @click="signOut"
        >
          Sign out
        </button>
      </div>
    </aside>

    <div class="lg:pl-60">
      <header class="sticky top-0 z-30 flex h-14 items-center justify-between gap-3 border-b border-line bg-card px-4 lg:hidden">
        <div class="min-w-0">
          <p class="truncate text-sm font-medium">{{ practice.data?.name || "Paw Lodge" }}</p>
        </div>
        <p class="truncate text-sm text-muted">{{ firstName }}</p>
      </header>

      <main id="main" class="mx-auto w-full max-w-6xl px-4 py-5 pb-28 sm:px-6 lg:px-8 lg:py-8 lg:pb-10">
        <RouterView />
      </main>
    </div>

    <nav
      aria-label="Primary"
      class="fixed inset-x-0 bottom-0 z-30 border-t border-line bg-card pb-[env(safe-area-inset-bottom)] lg:hidden"
    >
      <ul class="grid grid-cols-4">
        <li v-for="item in bottom" :key="item.to">
          <RouterLink
            :to="item.to"
            class="flex min-h-16 flex-col items-center justify-center gap-1 text-xs"
            :class="active(item.to) ? 'text-leaf' : 'text-muted'"
            :aria-current="active(item.to) ? 'page' : undefined"
          >
            <NavIcon :name="item.icon" />
            {{ item.label }}
          </RouterLink>
        </li>
        <li>
          <button
            type="button"
            class="flex min-h-16 w-full flex-col items-center justify-center gap-1 text-xs"
            :class="moreActive || shell.moreOpen ? 'text-leaf' : 'text-muted'"
            :aria-expanded="shell.moreOpen"
            aria-controls="more-menu"
            @click="shell.moreOpen = true"
          >
            <span class="text-base leading-none" aria-hidden="true">•••</span>
            More
          </button>
        </li>
      </ul>
    </nav>

    <Drawer :open="shell.moreOpen" title="More" @close="shell.moreOpen = false">
      <nav id="more-menu" aria-label="More" class="grid gap-1">
        <RouterLink
          v-for="item in moreLinks"
          :key="item.to"
          :to="item.to"
          class="flex min-h-12 items-center gap-3 rounded-xl px-3 text-sm"
          :class="active(item.to) ? 'bg-paper font-medium' : ''"
          :aria-current="active(item.to) ? 'page' : undefined"
          @click="shell.moreOpen = false"
        >
          <NavIcon :name="item.icon" />
          {{ item.label }}
        </RouterLink>
        <button
          type="button"
          class="mt-4 flex min-h-12 items-center rounded-xl px-3 text-left text-sm"
          @click="signOut"
        >
          Sign out
        </button>
      </nav>
    </Drawer>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { useRoute, useRouter } from "vue-router"

import { ApiError, errorMessage } from "../api/errors"
import AppButton from "../components/AppButton.vue"
import AppField from "../components/AppField.vue"
import AppInput from "../components/AppInput.vue"
import AuthFrame from "../components/AuthFrame.vue"
import { presentMutation } from "../lib/present"
import { useLogin } from "../queries/useSession"

const route = useRoute()
const router = useRouter()
const login = presentMutation(useLogin())

const email = ref("")
const password = ref("")
const errors = ref<Record<string, string>>({})
const formError = ref("")

async function onSubmit() {
  errors.value = {}
  formError.value = ""
  if (!email.value.trim()) errors.value.email = "Enter your email."
  if (!password.value) errors.value.password = "Enter your password."
  if (Object.keys(errors.value).length) return
  try {
    await login.mutateAsync({ email: email.value.trim(), password: password.value })
    await router.push("/app/dashboard")
  } catch (error) {
    if (error instanceof ApiError && Object.keys(error.fields).length) errors.value = error.fields
    else formError.value = errorMessage(error)
  }
}
</script>

<template>
  <AuthFrame>
    <h1 class="font-serif text-3xl text-ink">Sign in</h1>
    <p class="mt-2 text-sm text-muted">Use the email for your clinic account.</p>
    <p
      v-if="route.query.expired === '1'"
      class="mt-4 rounded-xl bg-warn-bg px-3 py-2 text-sm text-warn"
      role="status"
    >
      Your session ended. Sign in again.
    </p>
    <form class="mt-6 grid gap-4" @submit.prevent="onSubmit">
      <p v-if="formError" class="rounded-xl bg-danger-bg px-3 py-2 text-sm text-danger" role="alert">{{ formError }}</p>
      <AppField label="Email" field-id="login-email" :error="errors.email">
        <AppInput
          id="login-email"
          v-model="email"
          type="email"
          autocomplete="username"
          :invalid="Boolean(errors.email)"
        />
      </AppField>
      <AppField label="Password" field-id="login-password" :error="errors.password">
        <AppInput
          id="login-password"
          v-model="password"
          type="password"
          autocomplete="current-password"
          :invalid="Boolean(errors.password)"
        />
      </AppField>
      <AppButton type="submit" block :disabled="login.isPending">
        {{ login.isPending ? "Signing in…" : "Log in" }}
      </AppButton>
    </form>
    <p class="mt-6 text-sm text-muted">
      New clinic?
      <RouterLink to="/register" class="font-medium text-leaf underline-offset-2 hover:underline">Create practice</RouterLink>
    </p>
  </AuthFrame>
</template>

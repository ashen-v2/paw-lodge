<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"

import { ApiError, errorMessage } from "../api/errors"
import AppButton from "../components/AppButton.vue"
import AppField from "../components/AppField.vue"
import AppInput from "../components/AppInput.vue"
import AuthFrame from "../components/AuthFrame.vue"
import { presentMutation } from "../lib/present"
import { useRegister } from "../queries/useSession"

const router = useRouter()
const register = presentMutation(useRegister())

const practiceName = ref("")
const name = ref("")
const email = ref("")
const password = ref("")
const confirm = ref("")
const errors = ref<Record<string, string>>({})
const formError = ref("")

async function onSubmit() {
  errors.value = {}
  formError.value = ""
  if (!practiceName.value.trim()) errors.value.practice_name = "Enter the practice name."
  if (!name.value.trim()) errors.value.name = "Enter your name."
  if (!email.value.trim()) errors.value.email = "Enter your email."
  if (password.value.length < 8) errors.value.password = "Use at least 8 characters."
  if (password.value !== confirm.value) errors.value.confirm = "Passwords do not match."
  if (Object.keys(errors.value).length) return
  try {
    await register.mutateAsync({
      practice_name: practiceName.value.trim(),
      name: name.value.trim(),
      email: email.value.trim(),
      password: password.value,
    })
    await router.push("/app/dashboard")
  } catch (error) {
    if (error instanceof ApiError && error.status === 409) errors.value.email = error.message
    else if (error instanceof ApiError && Object.keys(error.fields).length) errors.value = error.fields
    else formError.value = errorMessage(error)
  }
}
</script>

<template>
  <AuthFrame>
    <h1 class="font-serif text-3xl text-ink">Create a practice</h1>
    <p class="mt-2 text-sm text-muted">You’ll be signed in as soon as the practice is created.</p>
    <form class="mt-6 grid gap-4" @submit.prevent="onSubmit">
      <p v-if="formError" class="rounded-xl bg-danger-bg px-3 py-2 text-sm text-danger" role="alert">{{ formError }}</p>
      <AppField label="Practice name" field-id="register-practice" :error="errors.practice_name">
        <AppInput id="register-practice" v-model="practiceName" maxlength="255" :invalid="Boolean(errors.practice_name)" />
      </AppField>
      <AppField label="Your name" field-id="register-name" :error="errors.name">
        <AppInput id="register-name" v-model="name" autocomplete="name" maxlength="255" :invalid="Boolean(errors.name)" />
      </AppField>
      <AppField label="Email" field-id="register-email" :error="errors.email">
        <AppInput
          id="register-email"
          v-model="email"
          type="email"
          autocomplete="username"
          :invalid="Boolean(errors.email)"
        />
      </AppField>
      <AppField label="Password" field-id="register-password" :error="errors.password" hint="At least 8 characters.">
        <AppInput
          id="register-password"
          v-model="password"
          type="password"
          autocomplete="new-password"
          maxlength="128"
          :invalid="Boolean(errors.password)"
        />
      </AppField>
      <AppField label="Confirm password" field-id="register-confirm" :error="errors.confirm">
        <AppInput
          id="register-confirm"
          v-model="confirm"
          type="password"
          autocomplete="new-password"
          maxlength="128"
          :invalid="Boolean(errors.confirm)"
        />
      </AppField>
      <AppButton type="submit" block :disabled="register.isPending">
        {{ register.isPending ? "Creating…" : "Create practice" }}
      </AppButton>
    </form>
    <p class="mt-6 text-sm text-muted">
      Already registered?
      <RouterLink to="/login" class="font-medium text-leaf underline-offset-2 hover:underline">Log in</RouterLink>
    </p>
  </AuthFrame>
</template>

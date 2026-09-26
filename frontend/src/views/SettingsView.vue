<script setup lang="ts">
import { ref, watch } from "vue"

import { ApiError, errorMessage } from "../api/errors"
import AppButton from "../components/AppButton.vue"
import AppField from "../components/AppField.vue"
import AppInput from "../components/AppInput.vue"
import AppTextarea from "../components/AppTextarea.vue"
import ErrorNotice from "../components/ErrorNotice.vue"
import PageHeader from "../components/PageHeader.vue"
import { blankToNull } from "../lib/form"
import { presentMutation, presentQuery } from "../lib/present"
import { roleLabel } from "../lib/dates"
import { toast } from "../lib/toast"
import { usePractice, useUpdatePractice } from "../queries/usePractice"
import { useMe } from "../queries/useSession"

const me = presentQuery(useMe())
const practice = presentQuery(usePractice())
const update = presentMutation(useUpdatePractice())

const name = ref("")
const phone = ref("")
const address = ref("")
const ready = ref(false)
const errors = ref<Record<string, string>>({})

const canEdit = () => me.data?.role === "owner"

watch(
  () => practice.data,
  (value) => {
    if (!value || ready.value) return
    name.value = value.name
    phone.value = value.phone ?? ""
    address.value = value.address ?? ""
    ready.value = true
  },
  { immediate: true },
)

async function onSubmit() {
  errors.value = {}
  if (!name.value.trim()) {
    errors.value.name = "Enter the practice name."
    return
  }
  try {
    await update.mutateAsync({
      name: name.value.trim(),
      phone: blankToNull(phone.value),
      address: blankToNull(address.value),
    })
    toast.success("Practice details saved.")
  } catch (error) {
    if (error instanceof ApiError && Object.keys(error.fields).length) errors.value = error.fields
    else toast.error(errorMessage(error))
  }
}
</script>

<template>
  <PageHeader title="Practice settings" description="Name, phone, and address shown for this clinic. The server has no currency setting, so amounts are shown in Rs." />

  <ErrorNotice v-if="practice.isError" :error="practice.error" @retry="practice.refetch()" />
  <form v-else class="max-w-xl rounded-2xl border border-line bg-card p-4" @submit.prevent="onSubmit">
    <p v-if="me.data && me.data.role !== 'owner'" class="mb-4 rounded-xl bg-warn-bg px-3 py-2 text-sm text-warn" role="status">
      You are signed in as {{ roleLabel(me.data.role) }}. Only the practice owner can change these details.
    </p>
    <fieldset class="grid gap-4" :disabled="me.data?.role !== 'owner'">
      <AppField label="Practice name" field-id="practice-name" :error="errors.name">
        <AppInput id="practice-name" v-model="name" maxlength="255" :invalid="Boolean(errors.name)" />
      </AppField>
      <AppField label="Phone" field-id="practice-phone" hint="Optional.">
        <AppInput id="practice-phone" v-model="phone" type="tel" maxlength="50" />
      </AppField>
      <AppField label="Address" field-id="practice-address" hint="Optional.">
        <AppTextarea id="practice-address" v-model="address" :rows="3" />
      </AppField>
      <AppButton v-if="canEdit()" type="submit" :disabled="update.isPending">
        {{ update.isPending ? "Saving…" : "Save settings" }}
      </AppButton>
    </fieldset>
  </form>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"

import { errorMessage } from "../api/errors"
import AppButton from "../components/AppButton.vue"
import AppField from "../components/AppField.vue"
import AppInput from "../components/AppInput.vue"
import AppSelect from "../components/AppSelect.vue"
import Badge from "../components/Badge.vue"
import Breadcrumb from "../components/Breadcrumb.vue"
import ErrorNotice from "../components/ErrorNotice.vue"
import PageHeader from "../components/PageHeader.vue"
import { askConfirm } from "../lib/confirm"
import { formatDate, formatDateTime } from "../lib/dates"
import { moneyInput } from "../lib/form"
import { formatMoney } from "../lib/money"
import { presentMutation, presentQuery } from "../lib/present"
import { methodLabel, visitPayStatus } from "../lib/status"
import { toast } from "../lib/toast"
import { usePets } from "../queries/usePets"
import { useCreatePayment, useDeleteVisit, useVisit } from "../queries/useVisits"

const route = useRoute()
const router = useRouter()
const visitId = computed(() => String(route.params.id ?? ""))
const visit = presentQuery(useVisit(visitId))
const blank = ref("")
const pets = presentQuery(usePets(blank, blank))
const createPayment = presentMutation(useCreatePayment())
const deleteVisit = presentMutation(useDeleteVisit())

const amount = ref("")
const method = ref<"cash" | "other">("cash")
const payError = ref("")

const petName = computed(() => pets.data?.find((pet) => pet.id === visit.data?.pet_id)?.name ?? "Pet")
const pay = computed(() =>
  visit.data
    ? visitPayStatus(Number(visit.data.outstanding), Boolean(visit.data.payment))
    : { tone: "neutral" as const, label: "" },
)

watch(
  () => visit.data,
  (value) => {
    if (!value || amount.value) return
    const due = Number(value.outstanding) > 0 ? Number(value.outstanding) : Number(value.total)
    amount.value = moneyInput(due)
  },
  { immediate: true },
)

async function onPay() {
  payError.value = ""
  if (!visit.data) return
  const value = Number(String(amount.value ?? "").trim())
  if (!Number.isFinite(value) || value <= 0) {
    payError.value = "Enter an amount greater than zero."
    return
  }
  try {
    await createPayment.mutateAsync({
      visit_id: visit.data.id,
      amount: amount.value,
      payment_method: method.value,
    })
    toast.success("Payment recorded.")
  } catch (error) {
    payError.value = errorMessage(error)
  }
}

async function onDelete() {
  if (!visit.data) return
  const ok = await askConfirm({
    title: "Delete this visit?",
    message: visit.data.payment
      ? "This cannot be undone. The payment recorded on this visit will be removed with it."
      : "This cannot be undone.",
    confirmLabel: "Delete visit",
  })
  if (!ok) return
  try {
    await deleteVisit.mutateAsync({ visitId: visit.data.id, petId: visit.data.pet_id })
    toast.success("Visit deleted.")
    await router.push("/app/visits")
  } catch (error) {
    toast.error(errorMessage(error))
  }
}
</script>

<template>
  <ErrorNotice v-if="visit.isError" :error="visit.error" @retry="visit.refetch()" />
  <template v-else-if="visit.data">
    <Breadcrumb :items="[{ label: 'Visits', to: '/app/visits' }, { label: formatDate(visit.data.visit_date) }]" />
    <PageHeader :title="visit.data.diagnosis || 'Visit'" :eyebrow="formatDate(visit.data.visit_date)">
      <template #actions>
        <Badge :tone="pay.tone">{{ pay.label }}</Badge>
      </template>
    </PageHeader>

    <p class="mb-4 text-sm">
      <RouterLink :to="`/app/pets/${visit.data.pet_id}`" class="text-leaf underline-offset-2 hover:underline">
        {{ petName }}
      </RouterLink>
      <span v-if="visit.data.follow_up_date" class="text-muted"> · Follow-up {{ formatDate(visit.data.follow_up_date) }}</span>
    </p>
    <p v-if="visit.data.notes" class="mb-4 whitespace-pre-wrap text-sm">{{ visit.data.notes }}</p>

    <section class="rounded-2xl border border-line bg-card p-4">
      <h2 class="font-serif text-2xl">Treatments</h2>
      <p class="mt-1 text-sm text-muted">Prices are the ones recorded on this visit.</p>
      <p v-if="visit.data.items.length === 0" class="mt-4 text-sm text-muted">No treatments on this visit.</p>
      <ul v-else class="mt-4 divide-y divide-line">
        <li v-for="item in visit.data.items" :key="item.id" class="flex items-start justify-between gap-3 py-3 text-sm">
          <span>
            <span class="block font-medium">{{ item.description }}</span>
            <span class="text-muted">{{ item.quantity }} × {{ formatMoney(item.unit_price) }}</span>
          </span>
          <span class="tabular-nums">{{ formatMoney(item.subtotal) }}</span>
        </li>
      </ul>
      <dl class="mt-4 grid gap-2 border-t border-line pt-4 text-sm sm:grid-cols-3">
        <div>
          <dt class="text-muted">Total</dt>
          <dd class="font-serif text-2xl tabular-nums">{{ formatMoney(visit.data.total) }}</dd>
        </div>
        <div>
          <dt class="text-muted">Paid</dt>
          <dd class="font-serif text-2xl tabular-nums">
            {{ formatMoney(visit.data.payment ? visit.data.payment.amount : 0) }}
          </dd>
        </div>
        <div>
          <dt class="text-muted">Outstanding</dt>
          <dd class="font-serif text-2xl tabular-nums">{{ formatMoney(visit.data.outstanding) }}</dd>
        </div>
      </dl>
    </section>

    <section class="mt-4 rounded-2xl border border-line bg-card p-4">
      <h2 class="font-serif text-2xl">Payment</h2>
      <div v-if="visit.data.payment" class="mt-3 text-sm">
        <p>
          {{ methodLabel(visit.data.payment.payment_method) }} · {{ formatMoney(visit.data.payment.amount) }}
        </p>
        <p class="mt-1 text-muted">Received {{ formatDateTime(visit.data.payment.paid_at) }}</p>
        <p v-if="Number(visit.data.outstanding) > 0.009" class="mt-3 rounded-xl bg-warn-bg px-3 py-2 text-warn">
          {{ formatMoney(visit.data.outstanding) }} is still outstanding. Another payment on this visit is not supported.
        </p>
      </div>
      <form v-else class="mt-4 grid gap-4 sm:max-w-md" @submit.prevent="onPay">
        <p v-if="payError" class="rounded-xl bg-danger-bg px-3 py-2 text-sm text-danger" role="alert">{{ payError }}</p>
        <AppField label="Amount" field-id="pay-amount">
          <AppInput id="pay-amount" v-model="amount" type="number" min="0.01" step="0.01" inputmode="decimal" />
        </AppField>
        <AppField label="Method" field-id="pay-method">
          <AppSelect id="pay-method" v-model="method">
            <option value="cash">Cash</option>
            <option value="other">Other</option>
          </AppSelect>
        </AppField>
        <AppButton type="submit" :disabled="createPayment.isPending">
          {{ createPayment.isPending ? "Saving…" : "Record payment" }}
        </AppButton>
      </form>
    </section>

    <AppButton class="mt-6" variant="danger" @click="onDelete">Delete visit</AppButton>
  </template>
</template>

<template>
  <div class="min-h-dvh lg:grid lg:grid-cols-[minmax(16rem,22rem)_1fr]">
    <aside class="hidden flex-col justify-between bg-spruce px-8 py-10 text-white lg:flex">
      <div>
        <p class="font-serif text-3xl">Paw Lodge</p>
        <p class="mt-4 max-w-xs text-sm leading-6 text-white/80">
          The day book for a small clinic. Owners, pets, visits, and the money, in one place.
        </p>
      </div>
      <p class="text-sm text-white/60">Built for the front desk and the exam room.</p>
    </aside>
    <main class="flex items-center justify-center px-4 py-10">
      <div class="w-full max-w-md">
        <p class="mb-6 font-serif text-3xl text-spruce lg:hidden">Paw Lodge</p>
        <slot />
      </div>
    </main>
  </div>
</template>

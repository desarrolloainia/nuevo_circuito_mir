<script setup lang="ts">
import { navigateTo, useHead, useToast } from '#imports'
import { CrearMirForm } from '@/features/crear-mir'

useHead({ title: 'Nuevo MIR · Circuito MIR' })

const toast = useToast()

async function onCreated() {
  toast.add({
    title: 'MIR creado',
    description: 'Ya está en revisión.',
    color: 'success',
    icon: 'i-lucide-check'
  })
  await navigateTo('/mis-mir')
}
</script>

<template>
  <main class="flex min-h-dvh flex-col px-6 py-8 sm:px-12 lg:py-10">
    <header
      class="flex items-center justify-between gap-4 opacity-0 animate-[fade-in-down_0.5s_ease-out_forwards]"
    >
      <span class="flex items-center gap-3 font-semibold tracking-tight">
        <UIcon
          name="i-lucide-workflow"
          class="size-5 transition-transform duration-300 hover:rotate-6"
          aria-hidden="true"
        />
        Circuito MIR
      </span>
      <UColorModeButton />
    </header>

    <section class="mx-auto w-full max-w-4xl flex-1 py-10">
      <UButton
        data-testid="volver-mis-mir"
        to="/mis-mir"
        variant="ghost"
        color="neutral"
        leading-icon="i-lucide-arrow-left"
        class="-ml-2.5 opacity-0 animate-[fade-in-up_0.5s_ease-out_0.1s_forwards]"
      >
        Volver a Mis MIR
      </UButton>
      <h1 class="mt-2 text-3xl font-semibold leading-tight tracking-tight opacity-0 sm:text-4xl animate-[fade-in-up_0.5s_ease-out_0.15s_forwards]">
        Nuevo MIR
      </h1>
      <p class="mt-4 max-w-md leading-relaxed text-muted opacity-0 animate-[fade-in-up_0.5s_ease-out_0.2s_forwards]">
        Reporta una incidencia, reclamación o mejora.
      </p>

      <div class="mt-8 opacity-0 animate-[fade-in-up_0.5s_ease-out_0.25s_forwards]">
        <CrearMirForm
          @created="onCreated"
          @cancel="navigateTo('/mis-mir')"
        />
      </div>
    </section>

    <footer class="text-xs text-muted">
      Circuito de calidad · MIR
    </footer>
  </main>
</template>

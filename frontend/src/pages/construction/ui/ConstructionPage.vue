<script setup lang="ts">
import { useHead } from '#imports'
import { clearUser, useCurrentUser } from '@/entities/user'

useHead({ title: 'En construcción · Circuito MIR' })
const user = useCurrentUser()
</script>

<template>
  <main class="flex min-h-dvh flex-col px-6 py-8 sm:px-12 lg:py-10">
    <header class="flex items-center justify-between gap-4">
      <span class="flex items-center gap-3 font-semibold tracking-tight">
        <UIcon
          name="i-lucide-workflow"
          class="size-5"
          aria-hidden="true"
        />
        Circuito MIR
      </span>
      <UColorModeButton />
    </header>
    <section
      class="mx-auto flex w-full max-w-xl flex-1 flex-col items-start justify-center py-16"
      aria-labelledby="construction-title"
    >
      <div class="mb-8 flex size-16 items-center justify-center rounded-2xl border border-default bg-elevated">
        <UIcon
          name="i-lucide-construction"
          class="size-8 text-muted"
          aria-hidden="true"
        />
      </div>
      <p class="mb-4 text-sm text-muted">
        Estamos preparando tu espacio de trabajo
      </p>
      <h1
        id="construction-title"
        class="text-4xl font-semibold leading-tight tracking-tight sm:text-5xl"
      >
        Todo está <br>en construcción
      </h1>
      <p class="mt-6 max-w-md leading-relaxed text-muted">
        El circuito MIR está tomando forma. Aquí podrás gestionar las incidencias, reclamaciones y mejoras de tu equipo.
      </p>
      <p
        v-if="user"
        class="mt-6 max-w-full break-all text-sm text-muted"
      >
        Has accedido como <span class="font-medium text-default">{{ user.correo }}</span>
      </p>
      <UButton
        to="/login"
        variant="outline"
        color="neutral"
        leading-icon="i-lucide-arrow-left"
        size="lg"
        class="mt-9"
        @click="clearUser"
      >
        Volver al acceso
      </UButton>
    </section>
    <footer class="text-xs text-muted">
      Circuito de calidad · MIR
    </footer>
  </main>
</template>

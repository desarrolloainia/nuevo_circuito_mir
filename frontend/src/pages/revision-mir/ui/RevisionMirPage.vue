<script setup lang="ts">
import { CerrarSesionButton } from '@/features/cerrar-sesion'
import { computed, h, onMounted, ref, resolveComponent } from 'vue'
import { useHead } from '#imports'
import { useCurrentUser } from '@/entities/user'
import { listMirsEnRevision, type MirRecord } from '@/entities/mir'
import type { TableColumn } from '@nuxt/ui'

useHead({ title: 'Pendientes de revisión · Circuito MIR' })

const user = useCurrentUser()

const mirs = ref<MirRecord[]>([])
const loading = ref(true)
const loadError = ref(false)

async function loadMirs(): Promise<void> {
  loading.value = true
  loadError.value = false
  try {
    mirs.value = await listMirsEnRevision()
  } catch {
    loadError.value = true
  } finally {
    loading.value = false
  }
}

onMounted(loadMirs)

// Cola FIFO: la que más tiempo lleva esperando va primero.
const pendientes = computed(() => [...mirs.value].sort((a, b) => a.creado_en.localeCompare(b.creado_en)))

const dateFormatter = new Intl.DateTimeFormat('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
const relativeFormatter = new Intl.RelativeTimeFormat('es-ES', { numeric: 'auto' })
const DAY_MS = 86_400_000

function waitingFor(isoDate: string): string {
  const days = Math.round((new Date(isoDate).getTime() - Date.now()) / DAY_MS)
  return relativeFormatter.format(days, 'day')
}

const masAntigua = computed(() => pendientes.value[0] ? waitingFor(pendientes.value[0].creado_en) : '—')

const nuxtLink = resolveComponent('NuxtLink')
const columns: TableColumn<MirRecord>[] = [
  {
    accessorKey: 'codigo_mir', header: 'Código',
    cell: ({ row }) => h(nuxtLink, { to: `/mir/${encodeURIComponent(row.original.codigo_mir)}`, class: 'font-mono font-medium text-primary hover:underline' }, () => row.original.codigo_mir)
  },
  { accessorKey: 'tipo', header: 'Tipo' },
  { accessorKey: 'prioridad', header: 'Prioridad', cell: ({ row }) => row.original.prioridad ?? '—' },
  { accessorKey: 'descripcion', header: 'Descripción', meta: { class: { td: 'max-w-md truncate' } } },
  {
    accessorKey: 'creado_en',
    header: 'Recibida',
    cell: ({ row }) => h('div', { class: 'tabular-nums' }, [
      h('span', dateFormatter.format(new Date(row.original.creado_en))),
      h('span', { class: 'block text-xs text-muted' }, waitingFor(row.original.creado_en))
    ])
  }
]
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
      <div class="flex items-center gap-1">
        <UColorModeButton />
        <CerrarSesionButton />
      </div>
    </header>

    <section class="mx-auto w-full max-w-4xl flex-1 py-10">
      <p
        v-if="user"
        class="text-sm text-muted opacity-0 animate-[fade-in-up_0.5s_ease-out_0.1s_forwards]"
      >
        Hola, <span class="font-medium text-default">{{ user.correo }}</span> · <span class="text-xs">Jefe de calidad</span>
      </p>
      <h1 class="mt-2 text-3xl font-semibold leading-tight tracking-tight opacity-0 sm:text-4xl animate-[fade-in-up_0.5s_ease-out_0.15s_forwards]">
        Pendientes de revisión
      </h1>
      <p class="mt-4 max-w-md leading-relaxed text-muted opacity-0 animate-[fade-in-up_0.5s_ease-out_0.2s_forwards]">
        MIR detectados que esperan tu revisión para asignarse o denegarse.
      </p>

      <dl class="mt-8 grid grid-cols-2 gap-6 border-y border-default py-6 opacity-0 sm:grid-cols-4 animate-[fade-in-up_0.5s_ease-out_0.25s_forwards]">
        <div>
          <dt class="text-xs text-muted">
            Pendientes
          </dt>
          <dd
            data-testid="total-pendientes"
            class="mt-1 text-2xl font-semibold tracking-tight tabular-nums text-warning transition-all duration-300"
          >
            {{ loading ? '—' : pendientes.length }}
          </dd>
        </div>
        <div>
          <dt class="text-xs text-muted">
            La más antigua
          </dt>
          <dd class="mt-1 text-2xl font-semibold tracking-tight">
            {{ loading ? '—' : masAntigua }}
          </dd>
        </div>
      </dl>

      <h2 class="mt-8 text-lg font-medium opacity-0 animate-[fade-in-up_0.5s_ease-out_0.3s_forwards]">
        Bandeja
      </h2>

      <div
        v-auto-animate
        class="opacity-0 animate-[fade-in-up_0.5s_ease-out_0.35s_forwards]"
      >
        <p
          v-if="loading"
          role="status"
          class="mt-4 text-sm text-muted"
        >
          Cargando MIR pendientes…
        </p>
        <div
          v-else-if="loadError"
          role="alert"
          class="mt-4 space-y-2 text-sm"
        >
          <p>No pudimos cargar las MIR pendientes. Inténtalo de nuevo.</p>
          <UButton
            data-testid="reintentar-revision-mir"
            variant="outline"
            color="neutral"
            @click="loadMirs"
          >
            Reintentar
          </UButton>
        </div>
        <UTable
          v-else-if="pendientes.length"
          :data="pendientes"
          :columns="columns"
          class="mt-4"
        />
        <div
          v-else
          class="mt-4 flex flex-col items-start rounded-lg border border-default bg-elevated px-6 py-10"
        >
          <UIcon
            name="i-lucide-inbox"
            class="size-6 text-muted"
            aria-hidden="true"
          />
          <p class="mt-3 text-sm text-muted">
            No hay MIR pendientes de revisión. Las nuevas detecciones aparecerán aquí.
          </p>
        </div>
      </div>
    </section>

    <footer class="text-xs text-muted">
      Circuito de calidad · MIR
    </footer>
  </main>
</template>

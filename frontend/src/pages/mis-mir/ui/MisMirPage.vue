<script setup lang="ts">
import { CerrarSesionButton } from '@/features/cerrar-sesion'
import { computed, h, onMounted, ref, resolveComponent } from 'vue'
import { useHead } from '#imports'
import { useCurrentUser } from '@/entities/user'
import { listMirsByDetector, MirEstadoBadge, type MirRecord } from '@/entities/mir'
import type { TableColumn } from '@nuxt/ui'

useHead({ title: 'Mis MIR · Circuito MIR' })

const user = useCurrentUser()

const misMirs = ref<MirRecord[]>([])
const loading = ref(true)
const loadError = ref(false)

async function loadMirs(): Promise<void> {
  loading.value = true
  loadError.value = false
  try {
    if (!user.value?.id) throw new Error('No hay detector seleccionado')
    misMirs.value = await listMirsByDetector(user.value.id)
  } catch {
    loadError.value = true
  } finally {
    loading.value = false
  }
}

onMounted(loadMirs)

const enRevision = computed(() => misMirs.value.filter(mir => mir.estado === 'EN_REVISION').length)
const enProgreso = computed(() => misMirs.value.filter(mir => mir.estado === 'EN_PROGRESO').length)
const terminadas = computed(() => misMirs.value.filter(mir => mir.estado === 'COMPLETADA' || mir.estado === 'TERMINADA').length)
const rechazadas = computed(() => misMirs.value.filter(mir => mir.estado === 'RECHAZADA').length)

const dateFormatter = new Intl.DateTimeFormat('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })

const nuxtLink = resolveComponent('NuxtLink')
const columns: TableColumn<MirRecord>[] = [
  {
    accessorKey: 'codigo_mir', header: 'Código',
    cell: ({ row }) => h(nuxtLink, { to: `/mir/${encodeURIComponent(row.original.codigo_mir)}`, class: 'font-mono font-medium text-primary hover:underline' }, () => row.original.codigo_mir)
  },
  { accessorKey: 'tipo', header: 'Tipo' },
  { accessorKey: 'descripcion', header: 'Descripción', meta: { class: { td: 'max-w-md truncate' } } },
  {
    accessorKey: 'estado',
    header: 'Estado',
    cell: ({ row }) => h(MirEstadoBadge, { estado: row.original.estado })
  },
  {
    accessorKey: 'creado_en',
    header: 'Fecha',
    cell: ({ row }) => dateFormatter.format(new Date(row.original.creado_en))
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
        Hola, <span class="font-medium text-default">{{ user.correo }}</span> · <span class="text-xs">Detector</span>
      </p>
      <h1 class="mt-2 text-3xl font-semibold leading-tight tracking-tight opacity-0 sm:text-4xl animate-[fade-in-up_0.5s_ease-out_0.15s_forwards]">
        Mis MIR
      </h1>
      <p class="mt-4 max-w-md leading-relaxed text-muted opacity-0 animate-[fade-in-up_0.5s_ease-out_0.2s_forwards]">
        Consulta el estado de las incidencias, reclamaciones y mejoras que has detectado.
      </p>

      <dl class="mt-8 grid grid-cols-2 gap-6 border-y border-default py-6 opacity-0 sm:grid-cols-4 animate-[fade-in-up_0.5s_ease-out_0.25s_forwards]">
        <div class="rounded-md transition-transform duration-200 hover:scale-[1.03]">
          <dt class="text-xs text-muted">
            En revisión
          </dt>
          <dd class="mt-1 text-2xl font-semibold tracking-tight text-warning transition-all duration-300">
            {{ enRevision }}
          </dd>
        </div>
        <div class="rounded-md transition-transform duration-200 hover:scale-[1.03]">
          <dt class="text-xs text-muted">
            En progreso
          </dt>
          <dd class="mt-1 text-2xl font-semibold tracking-tight transition-all duration-300">
            {{ enProgreso }}
          </dd>
        </div>
        <div class="rounded-md transition-transform duration-200 hover:scale-[1.03]">
          <dt class="text-xs text-muted">
            Terminadas
          </dt>
          <dd class="mt-1 text-2xl font-semibold tracking-tight text-success transition-all duration-300">
            {{ terminadas }}
          </dd>
        </div>
        <div>
          <dt class="text-xs text-muted">
            Rechazadas
          </dt>
          <dd class="mt-1 text-2xl font-semibold tracking-tight text-error">
            {{ rechazadas }}
          </dd>
        </div>
      </dl>

      <div class="mt-8 flex items-center justify-between gap-4 opacity-0 animate-[fade-in-up_0.5s_ease-out_0.3s_forwards]">
        <h2 class="text-lg font-medium">
          Historial
        </h2>
        <UButton
          data-testid="crear-mir"
          to="/detector/crear-mir"
          size="xl"
          leading-icon="i-lucide-plus"
          class="transition-transform duration-150 active:scale-95"
        >
          Crear MIR
        </UButton>
      </div>

      <div
        v-auto-animate
        class="opacity-0 animate-[fade-in-up_0.5s_ease-out_0.35s_forwards]"
      >
        <p
          v-if="loading"
          role="status"
          class="mt-4 text-sm text-muted"
        >
          Cargando tus MIR…
        </p>
        <div
          v-else-if="loadError"
          role="alert"
          class="mt-4 space-y-2 text-sm"
        >
          <p>No pudimos cargar tus MIR. Inténtalo de nuevo.</p>
          <UButton
            data-testid="reintentar-mis-mir"
            variant="outline"
            color="neutral"
            @click="loadMirs"
          >
            Reintentar
          </UButton>
        </div>
        <UTable
          v-else-if="misMirs.length"
          :data="misMirs"
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
            Todavía no has creado ningún MIR. Usa "Crear MIR" para reportar tu primera incidencia, reclamación o mejora.
          </p>
        </div>
      </div>
    </section>

    <footer class="text-xs text-muted">
      Circuito de calidad · MIR
    </footer>
  </main>
</template>

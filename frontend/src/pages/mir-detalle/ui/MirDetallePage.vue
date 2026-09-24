<script setup lang="ts">
import { CerrarSesionButton } from '@/features/cerrar-sesion'
import { computed, onMounted, ref } from 'vue'
import { useHead } from '#imports'
import { getMirByCode, MirEstadoBadge, type MirRecord } from '@/entities/mir'
import { homeForRol, useCurrentUser } from '@/entities/user'
import { RevisarMirPanel } from '@/features/revisar-mir'

const props = defineProps<{ codigoMir: string }>()
useHead({ title: `MIR ${props.codigoMir} · Circuito MIR` })

const user = useCurrentUser()
const home = homeForRol(user.value?.rol)
const mir = ref<MirRecord | null>(null)
const loading = ref(true)
const error = ref('')
const revisada = ref(false)
// El jefe de calidad decide en una columna lateral mientras la MIR esté en revisión (o justo tras decidir).
const showRevision = computed(() => user.value?.rol === 'JEFE_CLD' && (mir.value?.estado === 'EN_REVISION' || revisada.value))

function onRevisada(result: MirRecord): void {
  mir.value = result
  revisada.value = true
}

const dateFormatter = new Intl.DateTimeFormat('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })

async function loadMir(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    const result = await getMirByCode(props.codigoMir)
    if (user.value?.rol === 'DETECTOR' && result.detectada_por_id !== user.value.id) {
      mir.value = null
      error.value = 'No encontramos esta MIR entre tus registros.'
    } else {
      mir.value = result
    }
  } catch (cause: unknown) {
    const status = cause && typeof cause === 'object' && 'statusCode' in cause ? cause.statusCode : null
    error.value = status === 404 ? 'No encontramos esta MIR entre tus registros.' : 'No pudimos cargar esta MIR. Inténtalo de nuevo.'
  } finally {
    loading.value = false
  }
}

onMounted(loadMir)
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
      <div class="flex items-center gap-1">
        <UColorModeButton />
        <CerrarSesionButton />
      </div>
    </header>

    <section
      class="mx-auto w-full flex-1 py-10"
      :class="showRevision ? 'max-w-6xl' : 'max-w-4xl'"
    >
      <UButton
        :to="home"
        variant="ghost"
        color="neutral"
        leading-icon="i-lucide-arrow-left"
        class="-ml-2.5"
      >
        Volver
      </UButton>
      <p
        v-if="loading"
        role="status"
        class="mt-8 text-sm text-muted"
      >
        Cargando MIR…
      </p>
      <div
        v-else-if="error"
        role="alert"
        class="mt-8 space-y-3"
      >
        <p class="text-error">
          {{ error }}
        </p>
        <UButton
          v-if="error.startsWith('No pudimos')"
          data-testid="reintentar-detalle-mir"
          variant="outline"
          color="neutral"
          @click="loadMir"
        >
          Reintentar
        </UButton>
      </div>
      <div
        v-else-if="mir"
        :class="showRevision && 'lg:grid lg:grid-cols-[minmax(0,1fr)_20rem] lg:gap-12'"
      >
        <div class="min-w-0">
          <div class="mt-6 flex flex-wrap items-center gap-3">
            <h1 class="font-mono text-3xl font-semibold tracking-tight sm:text-4xl">
              MIR {{ mir.codigo_mir }}
            </h1>
            <MirEstadoBadge :estado="mir.estado" />
          </div>
          <p class="mt-3 text-sm text-muted">
            {{ mir.tipo }} · Registrada el {{ dateFormatter.format(new Date(mir.creado_en)) }}
          </p>

          <div class="mt-10 grid gap-8 border-t border-default pt-8 sm:grid-cols-2">
            <section>
              <h2 class="text-lg font-semibold">
                Detección
              </h2>
              <dl class="mt-4 space-y-3 text-sm">
                <div>
                  <dt class="text-muted">
                    Fecha de detección
                  </dt>
                  <dd>{{ mir.fecha_deteccion ? dateFormatter.format(new Date(`${mir.fecha_deteccion}T12:00:00`)) : 'No indicada' }}</dd>
                </div>
                <div>
                  <dt class="text-muted">
                    Solucionada en el registro
                  </dt>
                  <dd>{{ mir.solucionado ? 'Sí' : 'No' }}</dd>
                </div>
                <div>
                  <dt class="text-muted">
                    Prioridad
                  </dt>
                  <dd>{{ mir.prioridad ?? 'No asignada' }}</dd>
                </div>
              </dl>
            </section>
            <section>
              <h2 class="text-lg font-semibold">
                Datos del cliente
              </h2>
              <dl class="mt-4 space-y-3 text-sm">
                <div>
                  <dt class="text-muted">
                    Empresa
                  </dt>
                  <dd>{{ mir.empresa_nombre ?? 'No indicada' }}</dd>
                </div>
                <div>
                  <dt class="text-muted">
                    Persona de contacto
                  </dt>
                  <dd>{{ mir.persona_contacto ?? 'No indicada' }}</dd>
                </div>
                <div>
                  <dt class="text-muted">
                    Teléfono
                  </dt>
                  <dd>{{ mir.telefono ?? 'No indicado' }}</dd>
                </div>
                <div>
                  <dt class="text-muted">
                    Correo electrónico
                  </dt>
                  <dd>{{ mir.correo_electronico ?? 'No indicado' }}</dd>
                </div>
                <div v-if="mir.nombre_comercial">
                  <dt class="text-muted">
                    Nombre del comercial
                  </dt>
                  <dd>{{ mir.nombre_comercial }}</dd>
                </div>
                <div v-if="mir.codigo_cliente">
                  <dt class="text-muted">
                    Código cliente
                  </dt>
                  <dd>{{ mir.codigo_cliente }}</dd>
                </div>
              </dl>
            </section>
          </div>

          <section class="mt-8 border-t border-default pt-8">
            <h2 class="text-lg font-semibold">
              Descripción
            </h2>
            <p class="mt-3 max-w-prose whitespace-pre-wrap leading-relaxed">
              {{ mir.descripcion }}
            </p>
          </section>
          <section
            v-if="mir.solucionado"
            class="mt-8 border-t border-default pt-8"
          >
            <h2 class="text-lg font-semibold">
              Solución registrada
            </h2>
            <dl class="mt-4 space-y-4 text-sm">
              <div>
                <dt class="text-muted">
                  Solución adoptada
                </dt>
                <dd class="whitespace-pre-wrap">
                  {{ mir.solucion_adoptada }}
                </dd>
              </div>
              <div>
                <dt class="text-muted">
                  Análisis de causas
                </dt>
                <dd class="whitespace-pre-wrap">
                  {{ mir.analisis_causas }}
                </dd>
              </div>
              <div>
                <dt class="text-muted">
                  ¿Algo más que hacer?
                </dt>
                <dd class="whitespace-pre-wrap">
                  {{ mir.algo_mas_que_hacer }}
                </dd>
              </div>
            </dl>
          </section>
          <section class="mt-8 border-t border-default pt-8">
            <h2 class="text-lg font-semibold">
              Adjuntos
            </h2>
            <p class="mt-3 text-sm text-muted">
              {{ mir.documento_ids.length }} {{ mir.documento_ids.length === 1 ? 'archivo adjunto' : 'archivos adjuntos' }}
            </p>
          </section>
        </div>
        <aside
          v-if="showRevision"
          aria-label="Revisión"
          class="mt-10 self-start rounded-lg border border-default bg-elevated p-5 lg:sticky lg:top-10 lg:mt-6"
        >
          <RevisarMirPanel
            :mir="mir"
            @revisada="onRevisada"
          />
        </aside>
      </div>
    </section>
    <footer class="text-xs text-muted">
      Circuito de calidad · MIR
    </footer>
  </main>
</template>

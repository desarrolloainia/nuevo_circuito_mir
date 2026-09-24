<script setup lang="ts">
import { computed, ref } from 'vue'
import type { MirRecord } from '@/entities/mir'
import { homeForRol, listActiveUsers, useCurrentUser, type User } from '@/entities/user'
import { asignarTecnico, denegarMir } from '../api/revisar-mir'

const props = defineProps<{ mir: MirRecord }>()
const emit = defineEmits<{ revisada: [mir: MirRecord] }>()

type Paso = 'inicio' | 'aceptar' | 'rechazar' | 'hecho'

const user = useCurrentUser()
const bandeja = homeForRol(user.value?.rol)
const paso = ref<Paso>('inicio')
const sending = ref(false)
const error = ref('')
const resultado = ref('')

const tecnicos = ref<User[]>([])
const loadingTecnicos = ref(false)
const tecnicosError = ref(false)
const tecnicoId = ref<string>()

const tecnicoItems = computed(() => tecnicos.value.map(tecnico => ({
  label: tecnico.nombre,
  description: `${tecnico.correo} · ${tecnico.departamento}`,
  value: tecnico.id
})))

async function loadTecnicos(): Promise<void> {
  loadingTecnicos.value = true
  tecnicosError.value = false
  try {
    tecnicos.value = (await listActiveUsers()).filter(usuario => usuario.rol === 'TECNICO_CLD')
  } catch {
    tecnicosError.value = true
  } finally {
    loadingTecnicos.value = false
  }
}

function ir(siguiente: Paso): void {
  error.value = ''
  paso.value = siguiente
  if (siguiente === 'aceptar' && !tecnicos.value.length) loadTecnicos()
}

async function enviar(decision: () => Promise<MirRecord>, mensaje: () => string): Promise<void> {
  sending.value = true
  error.value = ''
  try {
    const mir = await decision()
    resultado.value = mensaje()
    paso.value = 'hecho'
    emit('revisada', mir)
  } catch (cause: unknown) {
    const status = cause && typeof cause === 'object' && 'statusCode' in cause ? cause.statusCode : null
    error.value = status === 422 && paso.value === 'aceptar'
      ? 'Ese usuario no es técnico de calidad. Elige otro.'
      : 'No pudimos enviar la decisión. Inténtalo de nuevo.'
  } finally {
    sending.value = false
  }
}

function confirmarRechazo(): Promise<void> {
  return enviar(
    () => denegarMir(props.mir.id, user.value!.id),
    () => `Rechazo enviado. La MIR ${props.mir.codigo_mir} ha quedado rechazada.`
  )
}

function confirmarAsignacion(): Promise<void> {
  const tecnico = tecnicos.value.find(t => t.id === tecnicoId.value)
  if (!tecnico) return Promise.resolve()
  return enviar(
    () => asignarTecnico(props.mir.id, tecnico.id),
    () => `MIR aceptada y asignada a ${tecnico.nombre}.`
  )
}
</script>

<template>
  <div v-auto-animate>
    <h2 class="text-lg font-semibold">
      Revisión
    </h2>

    <div
      v-if="paso === 'hecho'"
      key="hecho"
      role="status"
      class="mt-4"
    >
      <UIcon
        name="i-lucide-circle-check"
        class="size-6 text-success"
        aria-hidden="true"
      />
      <p class="mt-2 text-sm leading-relaxed">
        {{ resultado }}
      </p>
      <UButton
        :to="bandeja"
        variant="link"
        color="neutral"
        leading-icon="i-lucide-arrow-left"
        class="mt-3 px-0"
      >
        Volver a la bandeja
      </UButton>
    </div>

    <div
      v-else-if="paso === 'inicio'"
      key="inicio"
      class="mt-2"
    >
      <p class="text-sm text-muted">
        Decide si esta MIR sigue adelante.
      </p>
      <div class="mt-5 flex flex-col gap-2">
        <UButton
          block
          size="lg"
          leading-icon="i-lucide-user-check"
          class="transition-transform duration-150 active:scale-95"
          @click="ir('aceptar')"
        >
          Aceptar y asignar
        </UButton>
        <UButton
          block
          size="lg"
          color="error"
          variant="outline"
          leading-icon="i-lucide-x"
          class="transition-transform duration-150 active:scale-95"
          @click="ir('rechazar')"
        >
          Rechazar
        </UButton>
      </div>
    </div>

    <div
      v-else-if="paso === 'aceptar'"
      key="aceptar"
      class="mt-2"
    >
      <p class="text-sm text-muted">
        Elige el técnico de calidad que se encargará de ella.
      </p>
      <p
        v-if="loadingTecnicos"
        role="status"
        class="mt-4 text-sm text-muted"
      >
        Cargando técnicos…
      </p>
      <div
        v-else-if="tecnicosError"
        role="alert"
        class="mt-4 space-y-2 text-sm"
      >
        <p>No pudimos cargar los técnicos de calidad.</p>
        <UButton
          variant="outline"
          color="neutral"
          size="sm"
          @click="loadTecnicos"
        >
          Reintentar
        </UButton>
      </div>
      <p
        v-else-if="!tecnicos.length"
        class="mt-4 text-sm"
      >
        No hay técnicos de calidad activos. Da de alta uno antes de aceptar la MIR.
      </p>
      <UFormField
        v-else
        label="Técnico de calidad"
        class="mt-4"
      >
        <USelectMenu
          v-model="tecnicoId"
          :items="tecnicoItems"
          value-key="value"
          :filter-fields="['label', 'description']"
          :search-input="{ placeholder: 'Buscar por nombre o correo…' }"
          placeholder="Selecciona un técnico"
          size="lg"
          class="w-full"
          :disabled="sending"
        />
      </UFormField>
      <p
        v-if="error"
        role="alert"
        class="mt-3 text-sm text-error"
      >
        {{ error }}
      </p>
      <div class="mt-5 flex flex-col gap-2">
        <UButton
          block
          size="lg"
          :loading="sending"
          :disabled="!tecnicoId"
          @click="confirmarAsignacion"
        >
          Confirmar asignación
        </UButton>
        <UButton
          block
          variant="ghost"
          color="neutral"
          :disabled="sending"
          @click="ir('inicio')"
        >
          Cancelar
        </UButton>
      </div>
    </div>

    <div
      v-else
      key="rechazar"
      class="mt-2"
    >
      <p class="text-sm leading-relaxed">
        ¿Rechazar la MIR <span class="font-mono font-medium">{{ mir.codigo_mir }}</span>? No se podrá deshacer.
      </p>
      <p
        v-if="error"
        role="alert"
        class="mt-3 text-sm text-error"
      >
        {{ error }}
      </p>
      <div class="mt-5 flex flex-col gap-2">
        <UButton
          block
          size="lg"
          color="error"
          :loading="sending"
          @click="confirmarRechazo"
        >
          Sí, rechazar
        </UButton>
        <UButton
          block
          variant="ghost"
          color="neutral"
          :disabled="sending"
          @click="ir('inicio')"
        >
          Cancelar
        </UButton>
      </div>
    </div>
  </div>
</template>

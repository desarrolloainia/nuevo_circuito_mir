<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import type { FormError } from '@nuxt/ui'
import { listActiveUsers, useCurrentUser, type User } from '@/entities/user'
import { createMir } from '../api/create-mir'
import { createEmptyMirForm, validateCreateMir, TIPO_MIR_OPTIONS } from '../model/create-mir-form'

const emit = defineEmits<{ created: [], cancel: [] }>()

const currentUser = useCurrentUser()
const state = reactive(createEmptyMirForm(currentUser.value?.id ?? '', currentUser.value?.nombre ?? ''))
const pending = ref(false)
const error = ref('')
const users = ref<User[]>([])

onMounted(async () => {
  users.value = await listActiveUsers()
})

async function submit(): Promise<void> {
  if (pending.value) return
  error.value = ''
  pending.value = true
  try {
    await createMir(state)
    emit('created')
  } catch {
    error.value = 'No pudimos guardar el registro. Inténtalo de nuevo.'
  } finally {
    pending.value = false
  }
}

function validate(formState: typeof state): FormError[] {
  return validateCreateMir(formState)
}
</script>

<template>
  <UForm
    :state="state"
    :validate="validate"
    class="space-y-6"
    @submit="submit"
  >
    <UFormField
      label="Nombre"
      name="nombre"
      class="opacity-0 animate-[fade-in-up_0.5s_ease-out_forwards]"
    >
      <UInput
        v-model="state.nombre"
        name="nombre"
        size="xl"
        class="w-full"
        disabled
      />
    </UFormField>

    <div class="space-y-4 opacity-0 animate-[fade-in-up_0.5s_ease-out_0.05s_forwards]">
      <p class="text-xs font-medium tracking-widest text-muted uppercase">
        Detección
      </p>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <UFormField
          label="Tipo"
          name="tipo"
          required
        >
          <USelect
            v-model="state.tipo"
            :items="TIPO_MIR_OPTIONS"
            placeholder="Selecciona un tipo"
            size="xl"
            class="w-full"
            :disabled="pending"
          />
        </UFormField>
        <UFormField
          label="Fecha de detección"
          name="fechaDeteccion"
          required
        >
          <UInput
            v-model="state.fechaDeteccion"
            type="date"
            size="xl"
            class="w-full"
            :disabled="pending"
          />
        </UFormField>
        <UFormField
          label="Detectado por"
          name="detectadoPorId"
          required
        >
          <USelectMenu
            v-model="state.detectadoPorId"
            value-key="id"
            :items="users.map(currentUserOption => ({ label: currentUserOption.correo, id: currentUserOption.id }))"
            placeholder="Selecciona una persona"
            size="xl"
            class="w-full"
            :disabled="pending"
          />
        </UFormField>
      </div>
    </div>

    <div class="space-y-4 border-t border-default pt-6 opacity-0 animate-[fade-in-up_0.5s_ease-out_0.1s_forwards]">
      <p class="text-xs font-medium tracking-widest text-muted uppercase">
        Datos del cliente
      </p>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <UFormField
          label="Empresa"
          name="empresaNombre"
          required
        >
          <UInput
            v-model="state.empresaNombre"
            name="empresaNombre"
            placeholder="Nombre de la empresa"
            size="xl"
            class="w-full"
            :disabled="pending"
          />
        </UFormField>
        <UFormField
          label="Persona"
          name="personaContacto"
          required
        >
          <UInput
            v-model="state.personaContacto"
            name="personaContacto"
            placeholder="Persona de contacto"
            size="xl"
            class="w-full"
            :disabled="pending"
          />
        </UFormField>
        <UFormField
          label="Teléfono"
          name="telefono"
          required
        >
          <UInput
            v-model="state.telefono"
            name="telefono"
            type="tel"
            size="xl"
            class="w-full"
            :disabled="pending"
          />
        </UFormField>
        <UFormField
          label="Correo electrónico"
          name="correoElectronico"
          required
        >
          <UInput
            v-model="state.correoElectronico"
            name="correoElectronico"
            type="email"
            size="xl"
            class="w-full"
            :disabled="pending"
          />
        </UFormField>
        <UFormField
          label="Nombre del comercial"
          name="nombreComercial"
        >
          <UInput
            v-model="state.nombreComercial"
            name="nombreComercial"
            size="xl"
            class="w-full"
            :disabled="pending"
          />
        </UFormField>
        <UFormField
          label="Código cliente"
          name="codigoCliente"
        >
          <UInput
            v-model="state.codigoCliente"
            name="codigoCliente"
            size="xl"
            class="w-full"
            :disabled="pending"
          />
        </UFormField>
      </div>
    </div>

    <div class="space-y-4 border-t border-default pt-6 opacity-0 animate-[fade-in-up_0.5s_ease-out_0.15s_forwards]">
      <p class="text-xs font-medium tracking-widest text-muted uppercase">
        Detalle
      </p>
      <UFormField
        label="Descripción"
        name="descripcion"
        required
      >
        <UTextarea
          v-model="state.descripcion"
          :rows="4"
          size="xl"
          class="w-full max-w-prose"
          :disabled="pending"
        />
      </UFormField>
    </div>

    <div class="space-y-4 border-t border-default pt-6 opacity-0 animate-[fade-in-up_0.5s_ease-out_0.2s_forwards]">
      <p class="text-xs font-medium tracking-widest text-muted uppercase">
        Seguimiento
      </p>
      <UFormField
        label="¿Solucionada?"
        name="solucionada"
      >
        <USwitch
          v-model="state.solucionada"
          color="neutral"
          :disabled="pending"
        />
      </UFormField>
    </div>

    <div class="space-y-4 border-t border-default pt-6 opacity-0 animate-[fade-in-up_0.5s_ease-out_0.25s_forwards]">
      <p class="text-xs font-medium tracking-widest text-muted uppercase">
        Adjuntos
      </p>
      <UFileUpload
        v-model="state.archivos"
        multiple
        variant="area"
        layout="list"
        icon="i-lucide-paperclip"
        label="Arrastra archivos o haz clic para adjuntar"
        description="Cualquier formato, varios archivos"
        class="w-full"
        :disabled="pending"
      />
    </div>

    <UAlert
      v-if="pending"
      color="neutral"
      variant="soft"
      icon="i-lucide-loader-circle"
      title="Guardando tu MIR…"
      description="Esto tardará unos segundos."
      class="opacity-0 animate-[fade-in-up_0.3s_ease-out_forwards]"
    />
    <div
      v-else
      v-auto-animate
    >
      <p
        v-if="error"
        role="alert"
        class="text-sm leading-relaxed text-error"
      >
        {{ error }}
      </p>
    </div>

    <div class="flex justify-end gap-3">
      <UButton
        data-testid="cancelar-crear-mir"
        variant="ghost"
        color="neutral"
        size="xl"
        :disabled="pending"
        @click="emit('cancel')"
      >
        Cancelar
      </UButton>
      <UButton
        type="submit"
        size="xl"
        :loading="pending"
        :disabled="pending"
      >
        {{ pending ? 'Creando…' : 'Crear MIR' }}
      </UButton>
    </div>
  </UForm>
</template>

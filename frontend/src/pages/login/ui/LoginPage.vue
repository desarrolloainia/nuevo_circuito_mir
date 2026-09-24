<script setup lang="ts">
import { reactive, ref } from 'vue'
import { navigateTo, useHead } from '#imports'
import { getUserByEmail, homeForRol, registerUser, rememberUser } from '@/entities/user'
import { loginError, roleOptions, validateEmail, validateRegistration, type AccessState } from '../model/login'
import MirWorkflowIllustration from './MirWorkflowIllustration.vue'

useHead({ title: 'Acceso · Circuito MIR' })
const state = reactive<AccessState>({ email: '', nombre: '', department: '', role: 'DETECTOR' })
const mode = ref('login')
const pending = ref(false)
const error = ref('')

async function submit(): Promise<void> {
  if (pending.value) return
  error.value = ''
  pending.value = true
  try {
    const user = mode.value === 'register'
      ? await registerUser({ correo: state.email.trim(), nombre: state.nombre.trim(), departamento: state.department.trim(), rol: state.role })
      : await getUserByEmail(state.email.trim())
    if (!user.activo) {
      error.value = 'Tu usuario está dado de baja. Contacta con el administrador.'
      return
    }
    rememberUser(user)
    await navigateTo(homeForRol(user.rol))
  } catch (cause) {
    error.value = loginError(cause)
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <main class="grid min-h-dvh w-full lg:grid-cols-2">
    <section
      aria-labelledby="login-title"
      class="flex min-h-dvh min-w-0 flex-col px-[clamp(1.5rem,4vw,4rem)] py-[clamp(1.5rem,4dvh,2.5rem)]"
    >
      <header class="flex items-center justify-between gap-4">
        <span class="flex items-center gap-3 font-semibold tracking-tight">
          <span
            class="flex size-9 items-center justify-center rounded-lg border border-default"
            aria-hidden="true"
          >
            <UIcon
              name="i-lucide-workflow"
              class="size-5"
            />
          </span>
          Circuito <span class="font-normal text-muted">MIR</span>
        </span>
        <UColorModeButton />
      </header>

      <div class="mx-auto flex w-full max-w-96 flex-1 flex-col justify-center py-[clamp(2rem,6dvh,4rem)]">
        <h1
          id="login-title"
          class="text-3xl font-semibold leading-tight tracking-tight sm:text-4xl"
        >
          {{ mode === 'register' ? 'Crea tu usuario' : 'Accede al circuito MIR' }}
        </h1>
        <p class="mt-4 leading-relaxed text-muted">
          {{ mode === 'register' ? 'Únete al espacio de trabajo de tu equipo de calidad.' : 'Introduce tu correo corporativo para continuar.' }}
        </p>

        <UTabs
          v-model="mode"
          :items="[{ label: 'Acceder', value: 'login', disabled: pending }, { label: 'Registrarse', value: 'register', disabled: pending }]"
          color="neutral"
          variant="link"
          class="mt-6 w-full"
          :ui="{ trigger: 'flex-1 justify-center', content: 'pt-5' }"
          @update:model-value="error = ''"
        >
          <template #content>
            <UForm
              :key="mode"
              :state="state"
              :validate="mode === 'register' ? validateRegistration : validateEmail"
              class="space-y-5"
              @submit="submit"
            >
              <UFormField
                label="Correo corporativo"
                name="email"
                required
              >
                <UInput
                  v-model="state.email"
                  type="email"
                  autocomplete="email"
                  placeholder="nombre@empresa.es"
                  size="xl"
                  class="w-full"
                  :disabled="pending"
                  :aria-describedby="error ? 'login-error' : undefined"
                  @update:model-value="error = ''"
                />
              </UFormField>
              <template v-if="mode === 'register'">
                <UFormField
                  label="Nombre"
                  name="nombre"
                  required
                >
                  <UInput
                    v-model="state.nombre"
                    name="nombre"
                    type="text"
                    autocomplete="name"
                    placeholder="Tu nombre completo"
                    size="xl"
                    class="w-full"
                    :disabled="pending"
                    :aria-describedby="error ? 'login-error' : undefined"
                    @update:model-value="error = ''"
                  />
                </UFormField>
                <UFormField
                  label="Departamento"
                  name="department"
                  required
                >
                  <UInput
                    v-model="state.department"
                    name="department"
                    placeholder="Ej. Calidad"
                    size="xl"
                    class="w-full"
                    :disabled="pending"
                  />
                </UFormField>
                <UFormField
                  label="Rol"
                  name="role"
                  required
                >
                  <USelect
                    v-model="state.role"
                    :items="roleOptions"
                    size="xl"
                    class="w-full"
                    :disabled="pending"
                  />
                </UFormField>
              </template>
              <div v-auto-animate>
                <p
                  v-if="error"
                  id="login-error"
                  role="alert"
                  class="mb-5 text-sm leading-relaxed text-error"
                >
                  {{ error }}
                </p>
              </div>
              <UButton
                type="submit"
                size="xl"
                block
                :loading="pending"
                :disabled="pending"
                trailing-icon="i-lucide-arrow-right"
                class="justify-center"
              >
                {{ pending ? (mode === 'register' ? 'Creando usuario…' : 'Consultando…') : (mode === 'register' ? 'Crear usuario' : 'Continuar') }}
              </UButton>
            </UForm>
          </template>
        </UTabs>
        <p class="mt-6 text-sm leading-relaxed text-muted">
          {{ mode === 'register' ? 'Elige el rol que desempeñas en el circuito MIR.' : 'Utiliza el correo con el que estás registrado en tu equipo de calidad.' }}
        </p>
      </div>

      <footer class="flex items-center gap-2 text-xs text-muted">
        <UIcon
          name="i-lucide-building-2"
          class="size-4"
          aria-hidden="true"
        />
        Espacio de trabajo interno
      </footer>
    </section>

    <aside
      aria-labelledby="workflow-title"
      class="flex min-w-0 flex-col justify-center border-t border-default bg-elevated px-[clamp(1.5rem,4vw,4rem)] py-[clamp(1.5rem,4dvh,3rem)] lg:border-t-0 lg:border-l"
    >
      <div class="mx-auto w-full max-w-lg">
        <p class="mb-3 text-xs font-medium tracking-widest text-muted uppercase">
          El circuito de calidad
        </p>
        <h2
          id="workflow-title"
          class="text-3xl font-semibold leading-tight tracking-tight xl:text-4xl"
        >
          De la detección<br>al cierre.
        </h2>
        <p class="mt-4 max-w-sm leading-relaxed text-muted">
          Incidencias, reclamaciones y mejoras.<br>Un proceso compartido, paso a paso.
        </p>
        <MirWorkflowIllustration class="mt-[clamp(1.5rem,3dvh,2.5rem)]" />
        <p class="mt-5 border-t border-default pt-4 text-sm text-muted">
          Cada paso cuenta. Cada evidencia acompaña.
        </p>
      </div>
    </aside>
  </main>
</template>

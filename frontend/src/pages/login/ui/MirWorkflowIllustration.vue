<script setup lang="ts">
const steps = [
  { title: 'Detección', description: 'Identificar y registrar', icon: 'i-lucide-scan-search' },
  { title: 'Revisión', description: 'Analizar lo ocurrido', icon: 'i-lucide-clipboard-check' },
  { title: 'Asignación', description: 'Definir un responsable', icon: 'i-lucide-user-round-check' },
  { title: 'Resolución', description: 'Actuar sobre la causa', icon: 'i-lucide-wrench' },
  { title: 'Cierre', description: 'Verificar el resultado', icon: 'i-lucide-circle-check' }
]
</script>

<template>
  <div class="relative">
    <ol
      aria-label="Etapas del circuito MIR"
      class="workflow relative space-y-[clamp(0.75rem,2dvh,1.25rem)]"
    >
      <li
        v-for="(step, index) in steps"
        :key="step.title"
        class="workflow-step relative flex items-center gap-4"
        :style="{ '--step': index }"
      >
        <span
          class="relative z-1 flex size-11 shrink-0 items-center justify-center rounded-xl border bg-elevated"
          :class="index === 2 ? 'border-primary text-primary' : 'border-default text-muted'"
          aria-hidden="true"
        >
          <UIcon
            :name="step.icon"
            class="size-5"
          />
        </span>
        <div>
          <h3 class="font-medium">
            {{ step.title }}
          </h3>
          <p class="mt-0.5 text-sm text-muted">
            {{ step.description }}
          </p>
        </div>
      </li>
    </ol>
    <div class="mt-6 flex items-center gap-3 rounded-lg border border-dashed border-default px-4 py-3 text-muted">
      <UIcon
        name="i-lucide-paperclip"
        class="size-5 shrink-0"
        aria-hidden="true"
      />
      <p class="text-sm">
        <span class="font-medium text-default">Evidencias</span><br>Documentos e imágenes a lo largo del proceso
      </p>
    </div>
  </div>
</template>

<style scoped>
.workflow::before {
  content: '';
  position: absolute;
  left: 21px;
  top: 22px;
  bottom: 22px;
  width: 1px;
  background: var(--ui-border);
}

@media (prefers-reduced-motion: no-preference) {
  .workflow-step { animation: arrive 450ms ease-out both; animation-delay: calc(var(--step) * 100ms); }
}

@keyframes arrive {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

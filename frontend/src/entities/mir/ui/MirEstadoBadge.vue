<script setup lang="ts">
import { computed } from 'vue'
import { ESTADO_MIR_COLOR, ESTADO_MIR_LABEL, type EstadoMir } from '../model/mir'

const props = defineProps<{ estado: EstadoMir }>()

const label = computed(() => ESTADO_MIR_LABEL[props.estado])
const color = computed(() => ESTADO_MIR_COLOR[props.estado])
</script>

<template>
  <UBadge
    :color="color"
    variant="subtle"
    size="md"
  >
    {{ label }}
  </UBadge>
</template>

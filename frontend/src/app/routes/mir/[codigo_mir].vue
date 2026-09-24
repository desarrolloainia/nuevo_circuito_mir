<script setup lang="ts">
import { useRoute } from '#imports'
import { MirDetallePage } from '@/pages/mir-detalle'
import userContext from '../../model/user-context'

definePageMeta({ middleware: userContext })
const route = useRoute()
</script>

<template>
  <MirDetallePage :codigo-mir="String(route.params.codigo_mir)" />
</template>

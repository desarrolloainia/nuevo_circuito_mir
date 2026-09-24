<script setup lang="ts">
import { CrearMirPage } from '@/pages/crear-mir'
import userContext from '../../model/user-context'

definePageMeta({ middleware: userContext, rol: 'DETECTOR' })
</script>

<template>
  <CrearMirPage />
</template>

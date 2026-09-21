<script setup lang="ts">
import { CrearMirPage } from '@/pages/crear-mir'
import userContext from '../model/user-context'

definePageMeta({ middleware: userContext })
</script>

<template>
  <CrearMirPage />
</template>

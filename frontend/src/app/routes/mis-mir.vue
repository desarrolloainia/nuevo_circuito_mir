<script setup lang="ts">
import { MisMirPage } from '@/pages/mis-mir'
import userContext from '../model/user-context'

definePageMeta({ middleware: userContext })
</script>

<template>
  <MisMirPage />
</template>

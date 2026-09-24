<script setup lang="ts">
import { RevisionMirPage } from '@/pages/revision-mir'
import userContext from '../../model/user-context'

definePageMeta({ middleware: userContext, rol: 'JEFE_CLD' })
</script>

<template>
  <RevisionMirPage />
</template>

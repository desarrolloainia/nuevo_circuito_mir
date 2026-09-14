<script setup lang="ts">
import { ConstructionPage } from '@/pages/construction'
import userContext from '../model/user-context'

definePageMeta({ middleware: userContext })
</script>

<template>
  <ConstructionPage />
</template>

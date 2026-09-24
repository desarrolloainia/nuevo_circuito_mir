<script setup lang="ts">
import { navigateTo } from '#imports'
import { clearUser } from '@/entities/user'

function logout(): void {
  clearUser()
  navigateTo('/login')
}
</script>

<template>
  <UButton
    icon="i-lucide-log-out"
    color="neutral"
    variant="ghost"
    aria-label="Cerrar sesión"
    title="Cerrar sesión"
    @click="logout"
  />
</template>

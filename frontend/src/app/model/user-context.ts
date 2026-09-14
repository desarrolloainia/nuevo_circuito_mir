import { restoreUser, useCurrentUser } from '@/entities/user'

export default defineNuxtRouteMiddleware(async () => {
  if (import.meta.server) return
  if (useCurrentUser().value?.activo) return
  if (!await restoreUser()) return navigateTo('/login')
})

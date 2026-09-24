import { homeForRol, restoreUser, useCurrentUser, type Rol } from '@/entities/user'

declare module '#app' {
  interface PageMeta {
    // Rol dueño de la ruta; si no se indica, basta con tener sesión.
    rol?: Rol
  }
}

export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) return
  const user = useCurrentUser().value?.activo ? useCurrentUser().value : await restoreUser()
  if (!user) return navigateTo('/login')
  if (to.meta.rol && user.rol !== to.meta.rol) return navigateTo(homeForRol(user.rol))
})

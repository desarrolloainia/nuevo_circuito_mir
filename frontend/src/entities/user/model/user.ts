import { useState } from '#imports'
import { getUserByEmail } from '../api/get-user-by-email'
import type { components } from '@/shared/schema'

type User = components['schemas']['UsuarioRead']

export const useCurrentUser = () => useState<User | null>('mir-user', () => null)

export function rememberUser(user: User): void {
  useCurrentUser().value = user
  // El almacenamiento puede estar deshabilitado; el acceso en memoria sigue funcionando.
  try {
    sessionStorage.setItem('mir-email', user.correo)
  } catch { /* Sin persistencia. */ }
}

export function clearUser(): void {
  useCurrentUser().value = null
  try {
    sessionStorage.removeItem('mir-email')
  } catch { /* Sin persistencia. */ }
}

export async function restoreUser(): Promise<User | null> {
  const current = useCurrentUser()
  let email: string | null
  try {
    email = sessionStorage.getItem('mir-email')
  } catch {
    return current.value
  }
  if (!email) return current.value
  try {
    const user = await getUserByEmail(email)
    if (user.activo) {
      current.value = user
      return user
    }
  } catch {
    // Si no se puede verificar el usuario, se permite reintentar desde el acceso.
  }
  clearUser()
  return null
}

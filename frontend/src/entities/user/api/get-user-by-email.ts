import { apiGet } from '@/shared/api'
import type { components } from '@/shared/schema'

export function getUserByEmail(email: string): Promise<components['schemas']['UsuarioRead']> {
  return apiGet(`/usuarios/${encodeURIComponent(email)}`)
}

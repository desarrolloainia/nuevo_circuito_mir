import { apiDelete } from '@/shared/api'

export function deactivateUser(correo: string): Promise<void> {
  return apiDelete(`/usuarios/${encodeURIComponent(correo)}`)
}

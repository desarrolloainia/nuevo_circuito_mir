import { apiPatch } from '@/shared/api'
import type { ActualizarUsuario, User } from '../model/types'

export function updateUser(correo: string, data: ActualizarUsuario): Promise<User> {
  return apiPatch(`/usuarios/${encodeURIComponent(correo)}`, data)
}

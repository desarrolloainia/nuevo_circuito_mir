import { apiPost } from '@/shared/api'
import type { RegistrarUsuario, User } from '../model/types'

type Registration = Pick<RegistrarUsuario, 'correo' | 'nombre' | 'departamento' | 'rol'>

export function registerUser(data: Registration): Promise<User> {
  const body: RegistrarUsuario = {
    ...data,
    activo: true,
    creado_en: new Date().toISOString()
  }
  return apiPost('/usuarios', body)
}

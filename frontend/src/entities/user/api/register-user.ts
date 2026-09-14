import { apiPost } from '@/shared/api'
import type { components } from '@/shared/schema'

type Registration = Pick<components['schemas']['UsuarioRead'], 'correo' | 'departamento' | 'rol'>

export function registerUser(data: Registration): Promise<components['schemas']['UsuarioRead']> {
  const body: components['schemas']['RegistrarUsuarioDTO'] = {
    ...data,
    activo: true,
    creado_en: new Date().toISOString()
  }
  return apiPost('/usuarios', body)
}

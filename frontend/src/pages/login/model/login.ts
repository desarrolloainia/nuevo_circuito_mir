import type { FormError } from '@nuxt/ui'
import type { components } from '@/shared/schema'

export const roleOptions: { label: string, value: components['schemas']['Rol'] }[] = [
  { label: 'Detector', value: 'DETECTOR' },
  { label: 'Jefe CLD', value: 'JEFE_CLD' },
  { label: 'Técnico CLD', value: 'TECNICO_CLD' },
  { label: 'Responsable de resolución', value: 'RESPONSABLE_RESOLUCION' },
  { label: 'Ejecutor', value: 'EJECUTOR' },
  { label: 'RSGI', value: 'RSGI' }
]

export interface AccessState {
  email: string
  department: string
  role: components['schemas']['Rol']
}

export function validateEmail(state: { email: string }): FormError[] {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(state.email.trim())
    ? []
    : [{ name: 'email', message: 'Introduce un correo válido.' }]
}

export function loginError(error: unknown): string {
  const status = typeof error === 'object' && error !== null && 'statusCode' in error ? error.statusCode : undefined
  if (status === 404) return 'No encontramos un usuario con ese correo.'
  if (status === 409) return 'Este correo ya está registrado. Utiliza la pestaña Acceder.'
  if (status === 422) return 'Introduce un correo válido.'
  return 'No pudimos conectar con el servicio. Inténtalo de nuevo.'
}

export function validateRegistration(state: AccessState): FormError[] {
  const errors = validateEmail(state)
  if (!state.department.trim()) errors.push({ name: 'department', message: 'Introduce tu departamento.' })
  if (!roleOptions.some(option => option.value === state.role)) errors.push({ name: 'role', message: 'Selecciona un rol válido.' })
  return errors
}

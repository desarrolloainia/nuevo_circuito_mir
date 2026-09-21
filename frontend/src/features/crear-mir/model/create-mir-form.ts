import type { FormError } from '@nuxt/ui'
import type { TipoMir } from '@/entities/mir'

export const TIPO_MIR_OPTIONS: { label: string, value: TipoMir }[] = [
  { label: 'Mejora', value: 'Mejora' },
  { label: 'Incidencia', value: 'Incidencia' },
  { label: 'Reclamación', value: 'Reclamación' }
]

export interface CreateMirFormState {
  nombre: string
  tipo: TipoMir | undefined
  usuarioId: string
  fechaDeteccion: string
  detectadoPorId: string
  descripcion: string
  solucionada: boolean
  empresaNombre: string
  personaContacto: string
  telefono: string
  correoElectronico: string
  nombreComercial: string
  codigoCliente: string
  archivos: File[]
}

export function createEmptyMirForm(usuarioId: string, nombre: string): CreateMirFormState {
  return {
    nombre,
    tipo: undefined,
    usuarioId,
    fechaDeteccion: '',
    detectadoPorId: usuarioId,
    descripcion: '',
    solucionada: false,
    empresaNombre: '',
    personaContacto: '',
    telefono: '',
    correoElectronico: '',
    nombreComercial: '',
    codigoCliente: '',
    archivos: []
  }
}

export function validateCreateMir(state: CreateMirFormState): FormError[] {
  const errors: FormError[] = []
  if (!state.tipo) errors.push({ name: 'tipo', message: 'Selecciona el tipo de MIR.' })
  if (!state.fechaDeteccion) {
    errors.push({ name: 'fechaDeteccion', message: 'Indica la fecha de detección.' })
  } else if (new Date(state.fechaDeteccion) > new Date()) {
    errors.push({ name: 'fechaDeteccion', message: 'La fecha de detección no puede ser futura.' })
  }
  if (!state.detectadoPorId) errors.push({ name: 'detectadoPorId', message: 'Indica quién detectó el MIR.' })
  if (!state.descripcion.trim()) errors.push({ name: 'descripcion', message: 'Describe la mejora, incidencia o reclamación.' })
  if (!state.empresaNombre.trim()) errors.push({ name: 'empresaNombre', message: 'Indica el nombre de la empresa.' })
  if (!state.personaContacto.trim()) errors.push({ name: 'personaContacto', message: 'Indica la persona de contacto.' })
  if (!state.telefono.trim()) errors.push({ name: 'telefono', message: 'Indica un teléfono de contacto.' })
  if (!state.correoElectronico.trim()) errors.push({ name: 'correoElectronico', message: 'Indica un correo electrónico de contacto.' })
  return errors
}

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
  solucionAdoptada: string
  analisisCausas: string
  algoMasQueHacer: string
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
    solucionAdoptada: '',
    analisisCausas: '',
    algoMasQueHacer: '',
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
  } else if (state.fechaDeteccion > new Intl.DateTimeFormat('sv-SE', { timeZone: 'Europe/Madrid', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date())) {
    errors.push({ name: 'fechaDeteccion', message: 'La fecha de detección no puede ser futura.' })
  }
  if (!state.detectadoPorId) errors.push({ name: 'detectadoPorId', message: 'Indica quién detectó el MIR.' })
  if (!state.descripcion.trim()) errors.push({ name: 'descripcion', message: 'Describe la mejora, incidencia o reclamación.' })
  if (!state.empresaNombre.trim()) errors.push({ name: 'empresaNombre', message: 'Indica el nombre de la empresa.' })
  else if (state.empresaNombre.trim().length > 255) errors.push({ name: 'empresaNombre', message: 'El nombre de la empresa es demasiado largo.' })
  if (!state.personaContacto.trim()) errors.push({ name: 'personaContacto', message: 'Indica la persona de contacto.' })
  else if (state.personaContacto.trim().length > 255) errors.push({ name: 'personaContacto', message: 'La persona de contacto es demasiado larga.' })
  if (!state.telefono.trim()) errors.push({ name: 'telefono', message: 'Indica un teléfono de contacto.' })
  else if (state.telefono.trim().length > 50) errors.push({ name: 'telefono', message: 'El teléfono es demasiado largo.' })
  if (!state.correoElectronico.trim()) errors.push({ name: 'correoElectronico', message: 'Indica un correo electrónico de contacto.' })
  else if (state.correoElectronico.trim().length > 320 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(state.correoElectronico.trim())) {
    errors.push({ name: 'correoElectronico', message: 'El correo electrónico no es válido.' })
  }
  if (state.solucionada) {
    if (!state.solucionAdoptada.trim()) errors.push({ name: 'solucionAdoptada', message: 'Indica la solución adoptada.' })
    if (!state.analisisCausas.trim()) errors.push({ name: 'analisisCausas', message: 'Indica el análisis de causas.' })
    if (!state.algoMasQueHacer.trim()) errors.push({ name: 'algoMasQueHacer', message: 'Indica si queda algo más que hacer.' })
  }
  if (state.archivos.length > 10) errors.push({ name: 'archivos', message: 'Puedes adjuntar un máximo de diez archivos.' })
  return errors
}

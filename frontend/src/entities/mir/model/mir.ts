export type TipoMir = 'Mejora' | 'Incidencia' | 'Reclamación'

export type EstadoMir = 'EN_REVISION' | 'EN_PROGRESO' | 'COMPLETADA' | 'RECHAZADA' | 'TERMINADA'

export interface Mir {
  id: string
  tipo: TipoMir
  descripcion: string
  estado: EstadoMir
  creadoEn: string
}

export const ESTADO_MIR_LABEL: Record<EstadoMir, string> = {
  EN_REVISION: 'En revisión',
  EN_PROGRESO: 'En progreso',
  COMPLETADA: 'Completada',
  RECHAZADA: 'Rechazada',
  TERMINADA: 'Terminada'
}

// Colores semánticos de estado (nunca "primary"/naranja de marca, ver DESIGN.md "Regla del Naranja Escaso").
export const ESTADO_MIR_COLOR: Record<EstadoMir, 'warning' | 'success' | 'error' | 'neutral'> = {
  EN_REVISION: 'warning',
  EN_PROGRESO: 'neutral',
  COMPLETADA: 'success',
  RECHAZADA: 'error',
  TERMINADA: 'success'
}

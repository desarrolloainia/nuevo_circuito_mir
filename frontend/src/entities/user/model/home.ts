import type { Rol } from './types'

// Cada rol tiene su grupo de rutas (/detector, /jefe-calidad…) y una pantalla de inicio.
const HOME_BY_ROL: Partial<Record<Rol, string>> = {
  DETECTOR: '/detector/mis-mir',
  JEFE_CLD: '/jefe-calidad/revision-mir'
}

export function homeForRol(rol: Rol | null | undefined): string {
  return (rol && HOME_BY_ROL[rol]) ?? '/en-construccion'
}

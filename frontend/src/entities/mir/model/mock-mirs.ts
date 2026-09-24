import type { Mir } from './mir'

/**
 * Datos ficticios de desarrollo. Las pantallas usan la API real en entities/mir/api.
 */
export const MOCK_MIRS: Mir[] = [
  {
    id: '5b1f7b6e-2a86-4b5a-9b3b-9c2a3f8e1a01',
    tipo: 'Incidencia',
    descripcion: 'Fuga de aceite detectada en la línea de envasado 3 durante el turno de mañana.',
    estado: 'EN_PROGRESO',
    creadoEn: '2026-09-02T08:15:00Z'
  },
  {
    id: '5b1f7b6e-2a86-4b5a-9b3b-9c2a3f8e1a02',
    tipo: 'Reclamación',
    descripcion: 'Cliente reporta etiquetado incorrecto en el lote L-2245.',
    estado: 'EN_REVISION',
    creadoEn: '2026-09-08T11:40:00Z'
  },
  {
    id: '5b1f7b6e-2a86-4b5a-9b3b-9c2a3f8e1a03',
    tipo: 'Mejora',
    descripcion: 'Propuesta para automatizar el registro de temperatura en cámara frigorífica.',
    estado: 'TERMINADA',
    creadoEn: '2026-08-20T09:00:00Z'
  }
]

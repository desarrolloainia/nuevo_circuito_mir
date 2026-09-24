import { apiGet } from '@/shared/api'
import type { operations } from '@/shared/schema'

type MirList = operations['listar_jefe_calidad_mir_get']['responses'][200]['content']['application/json']

export function listMirsEnRevision(): Promise<MirList> {
  return apiGet<MirList>('/jefe-calidad/mir')
}

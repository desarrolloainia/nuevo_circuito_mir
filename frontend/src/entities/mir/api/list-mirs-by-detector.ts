import { apiGet } from '@/shared/api'
import type { operations } from '@/shared/schema'

type MirList = operations['listar_mir_get']['responses'][200]['content']['application/json']

export function listMirsByDetector(detectorId: string): Promise<MirList> {
  return apiGet<MirList>(`/mir?${new URLSearchParams({ detectada_por_id: detectorId })}`)
}

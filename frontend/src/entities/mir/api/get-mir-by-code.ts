import { apiGet } from '@/shared/api'
import type { operations } from '@/shared/schema'

type MirRecord = operations['consultar_mir__codigo_mir__get']['responses'][200]['content']['application/json']

export function getMirByCode(code: string): Promise<MirRecord> {
  return apiGet<MirRecord>(`/mir/${encodeURIComponent(code)}`)
}

import { apiPost } from '@/shared/api'
import type { operations } from '@/shared/schema'

type MirAsignada = operations['asignar_tecnico_jefe_calidad_mir__mir_id__asignar_tecnico_post']['responses'][200]['content']['application/json']
type MirDenegada = operations['denegar_jefe_calidad_mir__mir_id__denegar_post']['responses'][200]['content']['application/json']

export function asignarTecnico(mirId: string, tecnicoId: string): Promise<MirAsignada> {
  return apiPost<MirAsignada>(`/jefe-calidad/mir/${encodeURIComponent(mirId)}/asignar-tecnico`, { tecnico_cld_id: tecnicoId })
}

export function denegarMir(mirId: string, actorId: string): Promise<MirDenegada> {
  return apiPost<MirDenegada>(`/jefe-calidad/mir/${encodeURIComponent(mirId)}/denegar`, { actor_id: actorId })
}

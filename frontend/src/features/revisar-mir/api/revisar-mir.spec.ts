import { expect, it, vi } from 'vitest'
import { asignarTecnico, denegarMir } from './revisar-mir'

const { apiPost } = vi.hoisted(() => ({ apiPost: vi.fn() }))
vi.mock('@/shared/api', () => ({ apiPost }))

it('asigna la MIR al técnico de calidad elegido', async () => {
  const mir = { codigo_mir: '26001', estado: 'EN_PROGRESO' }
  apiPost.mockResolvedValue(mir)
  await expect(asignarTecnico('mir-1', 'tec-1')).resolves.toBe(mir)
  expect(apiPost).toHaveBeenCalledWith('/jefe-calidad/mir/mir-1/asignar-tecnico', { tecnico_cld_id: 'tec-1' })
})

it('deniega la MIR en nombre del jefe de calidad', async () => {
  const mir = { codigo_mir: '26001', estado: 'RECHAZADA' }
  apiPost.mockResolvedValue(mir)
  await expect(denegarMir('mir-1', 'jefe-1')).resolves.toBe(mir)
  expect(apiPost).toHaveBeenCalledWith('/jefe-calidad/mir/mir-1/denegar', { actor_id: 'jefe-1' })
})

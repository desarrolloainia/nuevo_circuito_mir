import { expect, it, vi } from 'vitest'
import { listMirsByDetector } from './list-mirs-by-detector'

const { apiGet } = vi.hoisted(() => ({ apiGet: vi.fn() }))
vi.mock('@/shared/api', () => ({ apiGet }))

it('consulta solo las MIR del detector indicado y devuelve la respuesta', async () => {
  const mirs = [{ codigo_mir: '26001' }]
  apiGet.mockResolvedValue(mirs)
  await expect(listMirsByDetector('detector-1')).resolves.toBe(mirs)
  expect(apiGet).toHaveBeenCalledWith('/mir?detectada_por_id=detector-1')
})

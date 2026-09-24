import { expect, it, vi } from 'vitest'
import { listMirsEnRevision } from './list-mirs-en-revision'

const { apiGet } = vi.hoisted(() => ({ apiGet: vi.fn() }))
vi.mock('@/shared/api', () => ({ apiGet }))

it('consulta las MIR pendientes de revisión del jefe de calidad', async () => {
  const mirs = [{ codigo_mir: '26001' }]
  apiGet.mockResolvedValue(mirs)
  await expect(listMirsEnRevision()).resolves.toBe(mirs)
  expect(apiGet).toHaveBeenCalledWith('/jefe-calidad/mir')
})

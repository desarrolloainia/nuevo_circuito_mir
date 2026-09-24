import { expect, it, vi } from 'vitest'
import { getMirByCode } from './get-mir-by-code'

const { apiGet } = vi.hoisted(() => ({ apiGet: vi.fn() }))
vi.mock('@/shared/api', () => ({ apiGet }))

it('consulta el detalle por código y codifica el segmento de la URL', async () => {
  const mir = { codigo_mir: '26/001' }
  apiGet.mockResolvedValue(mir)
  await expect(getMirByCode('26/001')).resolves.toBe(mir)
  expect(apiGet).toHaveBeenCalledWith('/mir/26%2F001')
})

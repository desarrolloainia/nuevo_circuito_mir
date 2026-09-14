import { expect, it, vi } from 'vitest'
import { getUserByEmail } from './get-user-by-email'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('@/shared/api', () => ({ apiGet: get }))

it('codifica el correo como un único parámetro de ruta', async () => {
  get.mockResolvedValue({ correo: 'auditor+mir@empresa.es' })
  await getUserByEmail('auditor+mir@empresa.es')
  expect(get).toHaveBeenCalledWith('/usuarios/auditor%2Bmir%40empresa.es')
})

import { expect, it, vi } from 'vitest'
import { listActiveUsers } from './list-active-users'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('@/shared/api', () => ({ apiGet: get }))

it('consulta la lista de usuarios activos', async () => {
  get.mockResolvedValue([{ correo: 'auditor@mir.es' }])
  await listActiveUsers()
  expect(get).toHaveBeenCalledWith('/usuarios')
})

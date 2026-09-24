import { mockNuxtImport } from '@nuxt/test-utils/runtime'
import { beforeEach, expect, it, vi } from 'vitest'
import type { RouteLocationNormalized } from 'vue-router'
import userContext from './user-context'

const { navigate, currentUser, restoreUser } = vi.hoisted(() => ({ navigate: vi.fn(), currentUser: { value: null as unknown }, restoreUser: vi.fn() }))
mockNuxtImport('navigateTo', () => navigate)
vi.mock('@/entities/user', async importOriginal => ({
  ...await importOriginal(),
  useCurrentUser: () => currentUser,
  restoreUser
}))

const run = (meta: Record<string, unknown> = {}) =>
  userContext({ meta } as RouteLocationNormalized, {} as RouteLocationNormalized)

beforeEach(() => {
  vi.clearAllMocks()
  currentUser.value = null
})

it('manda al acceso si no hay sesión', async () => {
  restoreUser.mockResolvedValue(null)
  await run()
  expect(navigate).toHaveBeenCalledWith('/login')
})

it('deja pasar a la ruta de su propio rol', async () => {
  currentUser.value = { activo: true, rol: 'JEFE_CLD' }
  await run({ rol: 'JEFE_CLD' })
  expect(navigate).not.toHaveBeenCalled()
})

it('devuelve a su pantalla a quien entra en la ruta de otro rol', async () => {
  currentUser.value = { activo: true, rol: 'DETECTOR' }
  await run({ rol: 'JEFE_CLD' })
  expect(navigate).toHaveBeenCalledWith('/detector/mis-mir')
})

import { beforeEach, expect, it, vi } from 'vitest'
import { clearUser, rememberUser, restoreUser } from './user'
import type { components } from '@/shared/schema'

const { lookup } = vi.hoisted(() => ({ lookup: vi.fn() }))
vi.mock('../api/get-user-by-email', () => ({ getUserByEmail: lookup }))
const user: components['schemas']['UsuarioRead'] = { id: '1', correo: 'auditor@mir.es', activo: true, rol: 'DETECTOR', departamento: 'Calidad', creado_en: '2026-09-14', dado_de_baja_en: null }

beforeEach(() => {
  clearUser()
  vi.clearAllMocks()
})

it('recuerda solo el correo y revalida el usuario al restaurar', async () => {
  rememberUser(user)
  lookup.mockResolvedValue(user)
  expect(await restoreUser()).toEqual(user)
  expect(lookup).toHaveBeenCalledWith(user.correo)
  clearUser()
  expect(await restoreUser()).toBeNull()
})

it('descarta el usuario si ha sido dado de baja', async () => {
  rememberUser(user)
  lookup.mockResolvedValue({ ...user, activo: false })
  expect(await restoreUser()).toBeNull()
  expect(sessionStorage.getItem('mir-email')).toBeNull()
})

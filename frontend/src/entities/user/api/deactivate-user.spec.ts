import { expect, it, vi } from 'vitest'
import { deactivateUser } from './deactivate-user'

const { del } = vi.hoisted(() => ({ del: vi.fn() }))
vi.mock('@/shared/api', () => ({ apiDelete: del }))

it('codifica el correo como parámetro de ruta al dar de baja', async () => {
  await deactivateUser('auditor+mir@empresa.es')
  expect(del).toHaveBeenCalledWith('/usuarios/auditor%2Bmir%40empresa.es')
})

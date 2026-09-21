import { expect, it, vi } from 'vitest'
import { updateUser } from './update-user'

const { patch } = vi.hoisted(() => ({ patch: vi.fn() }))
vi.mock('@/shared/api', () => ({ apiPatch: patch }))

it('codifica el correo y envía solo los campos a actualizar', async () => {
  await updateUser('auditor+mir@empresa.es', { rol: 'TECNICO_CLD' })
  expect(patch).toHaveBeenCalledWith('/usuarios/auditor%2Bmir%40empresa.es', { rol: 'TECNICO_CLD' })
})

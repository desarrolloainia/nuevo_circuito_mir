import { expect, it, vi } from 'vitest'
import { registerUser } from './register-user'

const { post } = vi.hoisted(() => ({ post: vi.fn() }))
vi.mock('@/shared/api', () => ({ apiPost: post }))

it('envía los campos requeridos por el contrato de registro, incluido el nombre', async () => {
  await registerUser({ correo: 'nuevo@mir.es', nombre: 'Ada Lovelace', departamento: 'Calidad', rol: 'DETECTOR' })
  expect(post).toHaveBeenCalledWith('/usuarios', {
    correo: 'nuevo@mir.es', nombre: 'Ada Lovelace', departamento: 'Calidad', rol: 'DETECTOR', activo: true, creado_en: expect.any(String)
  })
  expect(Number.isNaN(Date.parse(post.mock.calls[0]![1].creado_en))).toBe(false)
})

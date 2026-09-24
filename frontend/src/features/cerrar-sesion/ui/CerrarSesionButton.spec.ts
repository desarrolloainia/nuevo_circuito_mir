import { mockNuxtImport, mountSuspended } from '@nuxt/test-utils/runtime'
import { expect, it, vi } from 'vitest'
import CerrarSesionButton from './CerrarSesionButton.vue'

const { clearUser, navigateTo } = vi.hoisted(() => ({ clearUser: vi.fn(), navigateTo: vi.fn() }))

vi.mock('@/entities/user', async importOriginal => ({ ...await importOriginal(), clearUser }))
mockNuxtImport('navigateTo', () => navigateTo)

it('cierra la sesión y vuelve al acceso', async () => {
  const page = await mountSuspended(CerrarSesionButton)
  const button = page.find('button')
  expect(button.attributes('aria-label')).toBe('Cerrar sesión')

  await button.trigger('click')

  expect(clearUser).toHaveBeenCalledOnce()
  expect(navigateTo).toHaveBeenCalledWith('/login')
})

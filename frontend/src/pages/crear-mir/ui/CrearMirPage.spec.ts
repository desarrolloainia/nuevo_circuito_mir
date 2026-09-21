import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { ref } from 'vue'
import CrearMirPage from './CrearMirPage.vue'

const { listActiveUsers, createMir, navigate, toastAdd } = vi.hoisted(() => ({
  listActiveUsers: vi.fn(),
  createMir: vi.fn(),
  navigate: vi.fn(),
  toastAdd: vi.fn()
}))

vi.mock('@/entities/user', () => ({
  useCurrentUser: () => ref({ id: 'u-1', correo: 'ana@mir.es', nombre: 'Ana Auditora' }),
  listActiveUsers
}))
vi.mock('@/features/crear-mir/api/create-mir', () => ({ createMir }))
mockNuxtImport('navigateTo', () => navigate)
mockNuxtImport('useToast', () => () => ({ add: toastAdd }))

const mountPage = () => mountSuspended(CrearMirPage)

beforeEach(() => {
  vi.clearAllMocks()
  listActiveUsers.mockResolvedValue([{ id: 'u-1', correo: 'ana@mir.es' }])
  const matchMedia = window.matchMedia.bind(window)
  vi.spyOn(window, 'matchMedia').mockImplementation((query) => {
    const result = matchMedia(query)
    if (query === '(prefers-reduced-motion: reduce)') Object.defineProperty(result, 'matches', { value: true })
    return result
  })
})

afterEach(() => vi.restoreAllMocks())

it('presenta el formulario como pantalla, con título y enlace de vuelta al listado', async () => {
  const page = await mountPage()
  await flushPromises()
  expect(page.text()).toContain('Nuevo MIR')
  expect(page.get('[data-testid="volver-mis-mir"]').attributes('href')).toBe('/mis-mir')
  expect(page.find('textarea').exists()).toBe(true)
  page.unmount()
})

it('vuelve al listado sin avisar cuando se cancela', async () => {
  const page = await mountPage()
  await flushPromises()
  await page.get('[data-testid="cancelar-crear-mir"]').trigger('click')
  await flushPromises()
  expect(navigate).toHaveBeenCalledWith('/mis-mir')
  expect(toastAdd).not.toHaveBeenCalled()
  page.unmount()
})

it('confirma con un aviso y vuelve al listado cuando el MIR se ha creado', async () => {
  createMir.mockResolvedValue({ tipo: 'Incidencia' })
  const page = await mountPage()
  await flushPromises()

  const trigger = page.get('button[role="combobox"]')
  await trigger.trigger('keydown', { key: 'Enter' })
  await flushPromises()
  const option = Array.from(document.querySelectorAll('[role="option"]')).find(el => el.textContent?.trim() === 'Incidencia')
  option!.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true }))
  await flushPromises()
  await page.get('input[type="date"]').setValue('2026-01-10')
  await page.get('textarea').setValue('Fuga detectada en línea 3.')
  await page.get('input[placeholder="Nombre de la empresa"]').setValue('Ainia')
  await page.get('input[name="personaContacto"]').setValue('Marta Cliente')
  await page.get('input[name="telefono"]').setValue('600123456')
  await page.get('input[name="correoElectronico"]').setValue('marta@cliente.es')

  await page.get('form').trigger('submit')

  await vi.waitFor(() => expect(navigate).toHaveBeenCalledWith('/mis-mir'))
  expect(toastAdd).toHaveBeenCalledWith(expect.objectContaining({ title: 'MIR creado', color: 'success' }))
  page.unmount()
})

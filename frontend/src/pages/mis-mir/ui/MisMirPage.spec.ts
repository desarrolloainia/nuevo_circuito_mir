import { mountSuspended } from '@nuxt/test-utils/runtime'
import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { ref } from 'vue'
import MisMirPage from './MisMirPage.vue'

vi.mock('@/entities/user', () => ({
  useCurrentUser: () => ref({ id: 'u-1', correo: 'ana@mir.es', nombre: 'Ana Auditora', rol: 'DETECTOR' as const }),
  listActiveUsers: vi.fn().mockResolvedValue([{ id: 'u-1', correo: 'ana@mir.es' }])
}))

beforeEach(() => {
  const matchMedia = window.matchMedia.bind(window)
  vi.spyOn(window, 'matchMedia').mockImplementation((query) => {
    const result = matchMedia(query)
    if (query === '(prefers-reduced-motion: reduce)') Object.defineProperty(result, 'matches', { value: true })
    return result
  })
})

afterEach(() => vi.restoreAllMocks())

it('saluda al detector y muestra el resumen de estado de sus MIR', async () => {
  const page = await mountSuspended(MisMirPage)
  expect(page.text()).toContain('ana@mir.es')
  expect(page.text()).toContain('En revisión')
  expect(page.text()).toContain('En progreso')
  expect(page.text()).toContain('Terminadas')
  page.unmount()
})

it('lista las MIR del detector con su tipo, descripción y estado', async () => {
  const page = await mountSuspended(MisMirPage)
  expect(page.text()).toContain('Fuga de aceite detectada en la línea de envasado 3 durante el turno de mañana.')
  expect(page.text()).toContain('Incidencia')
  page.unmount()
})

it('lleva a la pantalla de creación en lugar de abrir un formulario aquí', async () => {
  const page = await mountSuspended(MisMirPage)
  await flushPromises()
  expect(page.get('[data-testid="crear-mir"]').attributes('href')).toBe('/crear-mir')
  expect(page.find('textarea').exists()).toBe(false)
  page.unmount()
})

import { mountSuspended } from '@nuxt/test-utils/runtime'
import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { ref } from 'vue'
import MisMirPage from './MisMirPage.vue'

const { listMirsByDetector } = vi.hoisted(() => ({ listMirsByDetector: vi.fn() }))

vi.mock('@/entities/user', () => ({
  useCurrentUser: () => ref({ id: 'u-1', correo: 'ana@mir.es', nombre: 'Ana Auditora', rol: 'DETECTOR' as const }),
  listActiveUsers: vi.fn().mockResolvedValue([{ id: 'u-1', correo: 'ana@mir.es' }])
}))
vi.mock('@/entities/mir', async importOriginal => ({ ...await importOriginal(), listMirsByDetector }))

const mirs = [
  { id: 'mir-1', codigo_mir: '26001', detectada_por_id: 'u-1', tipo: 'Incidencia', descripcion: 'Fuga de aceite ficticia.', estado: 'EN_PROGRESO', creado_en: '2026-09-02T08:15:00Z' },
  { id: 'mir-2', codigo_mir: '26002', detectada_por_id: 'u-1', tipo: 'Mejora', descripcion: 'Mejora ficticia.', estado: 'RECHAZADA', creado_en: '2026-09-08T11:40:00Z' }
]

beforeEach(() => {
  listMirsByDetector.mockReset()
  listMirsByDetector.mockResolvedValue(mirs)
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
  await vi.waitFor(() => expect(listMirsByDetector).toHaveBeenCalledWith('u-1'))
  expect(page.text()).toContain('ana@mir.es')
  expect(page.text()).toContain('En revisión')
  expect(page.text()).toContain('En progreso')
  expect(page.text()).toContain('Terminadas')
  expect(page.text()).toContain('Rechazadas')
  page.unmount()
})

it('lista las MIR del detector con su tipo, descripción y estado', async () => {
  const page = await mountSuspended(MisMirPage)
  await vi.waitFor(() => expect(page.text()).toContain('Fuga de aceite ficticia.'))
  expect(page.text()).toContain('Incidencia')
  expect(page.text()).toContain('26001')
  expect(page.get('a[href="/mir/26001"]').exists()).toBe(true)
  page.unmount()
})

it('muestra un estado vacío al no haber MIR reales', async () => {
  listMirsByDetector.mockResolvedValue([])
  const page = await mountSuspended(MisMirPage)
  await vi.waitFor(() => expect(page.text()).toContain('Todavía no has creado ningún MIR'))
  expect(page.text()).not.toContain('Fuga de aceite ficticia.')
  page.unmount()
})

it('avisa mientras espera la respuesta en lugar de mostrar el historial vacío', async () => {
  listMirsByDetector.mockImplementation(() => new Promise(() => {}))
  const page = await mountSuspended(MisMirPage)
  expect(page.get('[role="status"]').text()).toContain('Cargando tus MIR')
  expect(page.text()).not.toContain('Todavía no has creado ningún MIR')
  page.unmount()
})

it('muestra el fallo de carga y permite reintentar', async () => {
  listMirsByDetector.mockRejectedValueOnce(new Error('Error de red')).mockResolvedValueOnce(mirs)
  const page = await mountSuspended(MisMirPage)
  await vi.waitFor(() => expect(page.get('[role="alert"]').text()).toContain('No pudimos cargar'))
  await page.get('[data-testid="reintentar-mis-mir"]').trigger('click')
  await vi.waitFor(() => expect(page.text()).toContain('Fuga de aceite ficticia.'))
  expect(listMirsByDetector).toHaveBeenCalledTimes(2)
  page.unmount()
})

it('lleva a la pantalla de creación en lugar de abrir un formulario aquí', async () => {
  const page = await mountSuspended(MisMirPage)
  await flushPromises()
  expect(page.get('[data-testid="crear-mir"]').attributes('href')).toBe('/detector/crear-mir')
  expect(page.find('textarea').exists()).toBe(false)
  page.unmount()
})

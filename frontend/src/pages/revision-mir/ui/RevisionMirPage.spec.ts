import { mountSuspended } from '@nuxt/test-utils/runtime'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { ref } from 'vue'
import RevisionMirPage from './RevisionMirPage.vue'

const { listMirsEnRevision } = vi.hoisted(() => ({ listMirsEnRevision: vi.fn() }))

vi.mock('@/entities/user', () => ({
  useCurrentUser: () => ref({ id: 'j-1', correo: 'jefa@mir.es', rol: 'JEFE_CLD' as const })
}))
vi.mock('@/entities/mir', async importOriginal => ({ ...await importOriginal(), listMirsEnRevision }))

const mirs = [
  { id: 'mir-2', codigo_mir: '26002', tipo: 'Mejora', descripcion: 'Mejora ficticia reciente.', estado: 'EN_REVISION', prioridad: null, creado_en: '2026-09-20T11:40:00Z' },
  { id: 'mir-1', codigo_mir: '26001', tipo: 'Incidencia', descripcion: 'Fuga de aceite ficticia.', estado: 'EN_REVISION', prioridad: 'Alta', creado_en: '2026-09-02T08:15:00Z' }
]

beforeEach(() => {
  listMirsEnRevision.mockReset()
  listMirsEnRevision.mockResolvedValue(mirs)
  const matchMedia = window.matchMedia.bind(window)
  vi.spyOn(window, 'matchMedia').mockImplementation((query) => {
    const result = matchMedia(query)
    if (query === '(prefers-reduced-motion: reduce)') Object.defineProperty(result, 'matches', { value: true })
    return result
  })
})

afterEach(() => vi.restoreAllMocks())

it('saluda al jefe de calidad y cuenta las MIR pendientes', async () => {
  const page = await mountSuspended(RevisionMirPage)
  await vi.waitFor(() => expect(page.get('[data-testid="total-pendientes"]').text()).toBe('2'))
  expect(page.text()).toContain('jefa@mir.es')
  expect(page.text()).toContain('Pendientes de revisión')
  page.unmount()
})

it('lista las MIR en revisión de la más antigua a la más reciente', async () => {
  const page = await mountSuspended(RevisionMirPage)
  await vi.waitFor(() => expect(page.text()).toContain('Fuga de aceite ficticia.'))
  const links = page.findAll('tbody a').map(link => link.attributes('href'))
  expect(links).toEqual(['/mir/26001', '/mir/26002'])
  expect(page.text()).toContain('Alta')
  page.unmount()
})

it('muestra un estado vacío cuando no hay nada pendiente', async () => {
  listMirsEnRevision.mockResolvedValue([])
  const page = await mountSuspended(RevisionMirPage)
  await vi.waitFor(() => expect(page.text()).toContain('No hay MIR pendientes de revisión'))
  page.unmount()
})

it('avisa mientras espera la respuesta', async () => {
  listMirsEnRevision.mockImplementation(() => new Promise(() => {}))
  const page = await mountSuspended(RevisionMirPage)
  expect(page.get('[role="status"]').text()).toContain('Cargando')
  page.unmount()
})

it('muestra el fallo de carga y permite reintentar', async () => {
  listMirsEnRevision.mockRejectedValueOnce(new Error('Error de red')).mockResolvedValueOnce(mirs)
  const page = await mountSuspended(RevisionMirPage)
  await vi.waitFor(() => expect(page.get('[role="alert"]').text()).toContain('No pudimos cargar'))
  await page.get('[data-testid="reintentar-revision-mir"]').trigger('click')
  await vi.waitFor(() => expect(page.text()).toContain('Fuga de aceite ficticia.'))
  expect(listMirsEnRevision).toHaveBeenCalledTimes(2)
  page.unmount()
})

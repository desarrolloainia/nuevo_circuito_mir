import { mountSuspended } from '@nuxt/test-utils/runtime'
import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import RevisarMirPanel from './RevisarMirPanel.vue'

const { listActiveUsers, asignarTecnico, denegarMir } = vi.hoisted(() => ({
  listActiveUsers: vi.fn(),
  asignarTecnico: vi.fn(),
  denegarMir: vi.fn()
}))

vi.mock('@/entities/user', async importOriginal => ({
  ...await importOriginal(),
  useCurrentUser: () => ({ value: { id: 'jefe-1', rol: 'JEFE_CLD' } }),
  listActiveUsers
}))
vi.mock('../api/revisar-mir', () => ({ asignarTecnico, denegarMir }))

const mir = { id: 'mir-1', codigo_mir: '26001', estado: 'EN_REVISION' }
const usuarios = [
  { id: 'tec-1', nombre: 'Teresa Técnica', correo: 'teresa@mir.es', departamento: 'Calidad', rol: 'TECNICO_CLD' },
  { id: 'det-1', nombre: 'Diego Detector', correo: 'diego@mir.es', departamento: 'Planta', rol: 'DETECTOR' }
]

const mountPanel = () => mountSuspended(RevisarMirPanel, { props: { mir: mir as never } })
const button = (page: Awaited<ReturnType<typeof mountPanel>>, text: string) =>
  page.findAll('button').find(b => b.text().includes(text))!

beforeEach(() => {
  vi.clearAllMocks()
  listActiveUsers.mockResolvedValue(usuarios)
  const matchMedia = window.matchMedia.bind(window)
  vi.spyOn(window, 'matchMedia').mockImplementation((query) => {
    const result = matchMedia(query)
    if (query === '(prefers-reduced-motion: reduce)') Object.defineProperty(result, 'matches', { value: true })
    return result
  })
})

afterEach(() => vi.restoreAllMocks())

it('ofrece aceptar o rechazar la MIR', async () => {
  const page = await mountPanel()
  expect(button(page, 'Aceptar y asignar').exists()).toBe(true)
  expect(button(page, 'Rechazar').exists()).toBe(true)
  page.unmount()
})

it('pide confirmación antes de rechazar y no envía nada si se cancela', async () => {
  const page = await mountPanel()
  await button(page, 'Rechazar').trigger('click')
  expect(page.text()).toContain('¿Rechazar la MIR 26001?')
  await button(page, 'Cancelar').trigger('click')
  expect(denegarMir).not.toHaveBeenCalled()
  expect(button(page, 'Aceptar y asignar').exists()).toBe(true)
  page.unmount()
})

it('confirma que el rechazo se ha enviado', async () => {
  const rechazada = { ...mir, estado: 'RECHAZADA' }
  denegarMir.mockResolvedValue(rechazada)
  const page = await mountPanel()
  await button(page, 'Rechazar').trigger('click')
  await button(page, 'Sí, rechazar').trigger('click')
  await vi.waitFor(() => expect(page.get('[role="status"]').text()).toContain('Rechazo enviado'))
  expect(denegarMir).toHaveBeenCalledWith('mir-1', 'jefe-1')
  expect(page.emitted('revisada')).toEqual([[rechazada]])
  expect(page.get('a[href="/jefe-calidad/revision-mir"]').exists()).toBe(true)
  page.unmount()
})

it('al aceptar solo ofrece técnicos de calidad y exige elegir uno', async () => {
  const page = await mountPanel()
  await button(page, 'Aceptar y asignar').trigger('click')
  await flushPromises()
  const select = page.findComponent({ name: 'USelectMenu' })
  expect(select.props('items')).toEqual([{ label: 'Teresa Técnica', description: 'teresa@mir.es · Calidad', value: 'tec-1' }])
  expect(button(page, 'Confirmar asignación').attributes('disabled')).toBeDefined()
  page.unmount()
})

it('asigna la MIR al técnico elegido y lo confirma', async () => {
  const asignada = { ...mir, estado: 'EN_PROGRESO', tecnico_cld_id: 'tec-1' }
  asignarTecnico.mockResolvedValue(asignada)
  const page = await mountPanel()
  await button(page, 'Aceptar y asignar').trigger('click')
  await flushPromises()
  await page.findComponent({ name: 'USelectMenu' }).vm.$emit('update:modelValue', 'tec-1')
  await button(page, 'Confirmar asignación').trigger('click')
  await vi.waitFor(() => expect(page.get('[role="status"]').text()).toContain('asignada a Teresa Técnica'))
  expect(asignarTecnico).toHaveBeenCalledWith('mir-1', 'tec-1')
  expect(page.emitted('revisada')).toEqual([[asignada]])
  page.unmount()
})

it('avisa si no hay técnicos de calidad activos', async () => {
  listActiveUsers.mockResolvedValue([usuarios[1]])
  const page = await mountPanel()
  await button(page, 'Aceptar y asignar').trigger('click')
  await vi.waitFor(() => expect(page.text()).toContain('No hay técnicos de calidad activos'))
  page.unmount()
})

it('muestra el fallo del envío y mantiene la decisión abierta', async () => {
  asignarTecnico.mockRejectedValue({ statusCode: 422 })
  const page = await mountPanel()
  await button(page, 'Aceptar y asignar').trigger('click')
  await flushPromises()
  await page.findComponent({ name: 'USelectMenu' }).vm.$emit('update:modelValue', 'tec-1')
  await button(page, 'Confirmar asignación').trigger('click')
  await vi.waitFor(() => expect(page.get('[role="alert"]').text()).toContain('no es técnico de calidad'))
  expect(button(page, 'Confirmar asignación').exists()).toBe(true)
  expect(page.emitted('revisada')).toBeUndefined()
  page.unmount()
})

it('avisa si falla el rechazo', async () => {
  denegarMir.mockRejectedValue(new Error('Error de red'))
  const page = await mountPanel()
  await button(page, 'Rechazar').trigger('click')
  await button(page, 'Sí, rechazar').trigger('click')
  await vi.waitFor(() => expect(page.get('[role="alert"]').text()).toContain('No pudimos enviar la decisión'))
  page.unmount()
})

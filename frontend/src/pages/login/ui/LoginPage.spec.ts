import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import LoginPage from './LoginPage.vue'

const { lookup, register, navigate } = vi.hoisted(() => ({ lookup: vi.fn(), register: vi.fn(), navigate: vi.fn() }))
const mountPage = () => mountSuspended(LoginPage)
vi.mock('@/entities/user', async importOriginal => ({ ...await importOriginal(), getUserByEmail: lookup, registerUser: register, rememberUser: (user: { correo: string }) => sessionStorage.setItem('mir-email', user.correo) }))
mockNuxtImport('navigateTo', () => navigate)

beforeEach(() => {
  vi.clearAllMocks()
  sessionStorage.clear()
  const matchMedia = window.matchMedia.bind(window)
  vi.spyOn(window, 'matchMedia').mockImplementation((query) => {
    const result = matchMedia(query)
    if (query === '(prefers-reduced-motion: reduce)') Object.defineProperty(result, 'matches', { value: true })
    return result
  })
})

afterEach(() => vi.restoreAllMocks())

it('permite registrar un usuario y continuar al espacio de trabajo', async () => {
  register.mockResolvedValue({ correo: 'nuevo@mir.es', activo: true })
  const page = await mountPage()
  await page.findAll('[role="tab"]').find(tab => tab.text() === 'Registrarse')!.trigger('keydown', { key: 'Enter' })
  await page.get('input[type="email"]').setValue('nuevo@mir.es')
  await page.get('input[name="nombre"]').setValue(' Ada Lovelace ')
  await page.get('input[name="department"]').setValue(' Calidad ')
  await page.get('form').trigger('submit')
  await vi.waitFor(() => expect(register).toHaveBeenCalledWith({ correo: 'nuevo@mir.es', nombre: 'Ada Lovelace', departamento: 'Calidad', rol: 'DETECTOR' }))
  expect(navigate).toHaveBeenCalledWith('/en-construccion')
  expect(lookup).not.toHaveBeenCalled()
  page.unmount()
})

it('pide departamento y muestra el conflicto de un correo ya registrado', async () => {
  register.mockRejectedValue({ statusCode: 409 })
  const page = await mountPage()
  await page.findAll('[role="tab"]').find(tab => tab.text() === 'Registrarse')!.trigger('keydown', { key: 'Enter' })
  await page.get('input[type="email"]').setValue('nuevo@mir.es')
  await page.get('form').trigger('submit')
  await vi.waitFor(() => expect(page.text()).toContain('Introduce tu nombre'))
  expect(register).not.toHaveBeenCalled()
  await page.get('input[name="nombre"]').setValue('Ada Lovelace')
  await page.get('input[name="department"]').setValue('Calidad')
  await page.get('form').trigger('submit')
  await vi.waitFor(() => expect(page.text()).toContain('Este correo ya está registrado'))
  expect(navigate).not.toHaveBeenCalled()
  page.unmount()
})

it('rechaza el correo vacío sin consultar el servicio', async () => {
  const page = await mountPage()
  await page.get('form').trigger('submit')
  await vi.waitFor(() => expect(page.text()).toContain('Introduce un correo válido'))
  expect(lookup).not.toHaveBeenCalled()
  page.unmount()
})

it('bloquea envíos repetidos mientras consulta', async () => {
  let resolve: (value: { activo: boolean }) => void = () => {}
  lookup.mockImplementation(() => new Promise((done) => {
    resolve = done
  }))
  const page = await mountPage()
  await page.get('input').setValue('auditor@mir.es')
  await page.get('form').trigger('submit')
  await vi.waitFor(() => expect(page.text()).toContain('Consultando…'))
  expect(page.get('button[type="submit"]').attributes('disabled')).toBeDefined()
  await page.get('form').trigger('submit')
  await flushPromises()
  expect(lookup).toHaveBeenCalledTimes(1)
  resolve({ activo: false })
  await vi.waitFor(() => expect(page.text()).toContain('dado de baja'))
  page.unmount()
})

it('muestra el acceso y las cinco etapas del circuito', async () => {
  const page = await mountPage()
  expect(page.find('input[type="email"]').exists()).toBe(true)
  for (const label of ['Detección', 'Revisión', 'Asignación', 'Resolución', 'Cierre']) {
    expect(page.text()).toContain(label)
  }
  page.unmount()
})

it('consulta el correo y continúa con un usuario activo', async () => {
  lookup.mockResolvedValue({ correo: 'auditor@mir.es', activo: true })
  const page = await mountPage()
  await page.get('input').setValue('auditor@mir.es')
  await page.get('form').trigger('submit')
  await vi.waitFor(() => expect(navigate).toHaveBeenCalledWith('/en-construccion'))
  expect(lookup).toHaveBeenCalledWith('auditor@mir.es')
  expect(sessionStorage.getItem('mir-email')).toBe('auditor@mir.es')
  page.unmount()
})

it('impide continuar con un usuario inactivo', async () => {
  lookup.mockResolvedValue({ activo: false })
  const page = await mountPage()
  await page.get('input').setValue('auditor@mir.es')
  await page.get('form').trigger('submit')
  await vi.waitFor(() => expect(page.text()).toContain('dado de baja'))
  expect(navigate).not.toHaveBeenCalled()
  page.unmount()
})

it('muestra el error de consulta y conserva el correo', async () => {
  lookup.mockRejectedValue({ statusCode: 404 })
  const page = await mountPage()
  await page.get('input').setValue('auditor@mir.es')
  await page.get('form').trigger('submit')
  await vi.waitFor(() => expect(page.text()).toContain('No encontramos'))
  expect(page.get('input').element.value).toBe('auditor@mir.es')
  await flushPromises()
  page.unmount()
})

it('lleva al jefe de calidad a su bandeja de revisión', async () => {
  lookup.mockResolvedValue({ correo: 'jefa@mir.es', activo: true, rol: 'JEFE_CLD' })
  const page = await mountPage()
  await page.get('input').setValue('jefa@mir.es')
  await page.get('form').trigger('submit')
  await vi.waitFor(() => expect(navigate).toHaveBeenCalledWith('/jefe-calidad/revision-mir'))
  page.unmount()
})

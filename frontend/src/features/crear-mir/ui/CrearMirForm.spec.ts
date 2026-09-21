import { mountSuspended } from '@nuxt/test-utils/runtime'
import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { ref } from 'vue'
import CrearMirForm from './CrearMirForm.vue'

const { listActiveUsers, createMir } = vi.hoisted(() => ({ listActiveUsers: vi.fn(), createMir: vi.fn() }))

vi.mock('@/entities/user', () => ({
  useCurrentUser: () => ref({ id: 'u-1', correo: 'ana@mir.es', nombre: 'Ana Auditora' }),
  listActiveUsers
}))
vi.mock('../api/create-mir', () => ({ createMir }))

const mountForm = () => mountSuspended(CrearMirForm)

async function selectTipoIncidencia(form: Awaited<ReturnType<typeof mountForm>>): Promise<void> {
  const trigger = form.get('button[role="combobox"]')
  await trigger.trigger('keydown', { key: 'Enter' })
  await flushPromises()
  const option = Array.from(document.querySelectorAll('[role="option"]')).find(el => el.textContent?.trim() === 'Incidencia')
  option!.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true }))
  await flushPromises()
}

beforeEach(() => {
  vi.clearAllMocks()
  listActiveUsers.mockResolvedValue([
    { id: 'u-1', correo: 'ana@mir.es' },
    { id: 'u-2', correo: 'luis@mir.es' }
  ])
})

afterEach(() => vi.restoreAllMocks())

it('renderiza los campos principales y precarga el nombre del usuario logueado, deshabilitado', async () => {
  const form = await mountForm()
  await flushPromises()
  expect(form.find('textarea').exists()).toBe(true)
  expect(form.findAll('input').length).toBeGreaterThan(0)
  const nombreInput = form.get('input[name="nombre"]')
  expect((nombreInput.element as HTMLInputElement).value).toBe('Ana Auditora')
  expect(nombreInput.attributes('disabled')).toBeDefined()
  form.unmount()
})

it('no envía y muestra los errores de validación cuando el formulario está vacío', async () => {
  const form = await mountForm()
  await flushPromises()
  await form.get('form').trigger('submit')
  await vi.waitFor(() => expect(form.text()).toContain('Selecciona el tipo de MIR'))
  expect(createMir).not.toHaveBeenCalled()
  form.unmount()
})

async function fillValidForm(form: Awaited<ReturnType<typeof mountForm>>): Promise<void> {
  await selectTipoIncidencia(form)
  await form.get('input[type="date"]').setValue('2026-01-10')
  await form.get('textarea').setValue('Fuga detectada en línea 3.')
  await form.get('input[placeholder="Nombre de la empresa"]').setValue('Ainia')
  await form.get('input[name="personaContacto"]').setValue('Marta Cliente')
  await form.get('input[name="telefono"]').setValue('600123456')
  await form.get('input[name="correoElectronico"]').setValue('marta@cliente.es')
}

it('envía el formulario válido y emite created al resolver', async () => {
  createMir.mockResolvedValue({ tipo: 'Incidencia' })
  const form = await mountForm()
  await flushPromises()

  await fillValidForm(form)

  await form.get('form').trigger('submit')
  await vi.waitFor(() => expect(createMir).toHaveBeenCalledTimes(1))
  expect(createMir).toHaveBeenCalledWith(expect.objectContaining({
    tipo: 'Incidencia',
    fechaDeteccion: '2026-01-10',
    descripcion: 'Fuga detectada en línea 3.',
    empresaNombre: 'Ainia',
    personaContacto: 'Marta Cliente',
    telefono: '600123456',
    correoElectronico: 'marta@cliente.es',
    detectadoPorId: 'u-1'
  }))
  await vi.waitFor(() => expect(form.emitted('created')).toBeTruthy())
  form.unmount()
})

it('muestra un mensaje de progreso mientras se envía', async () => {
  createMir.mockImplementation(() => new Promise(() => {}))
  const form = await mountForm()
  await flushPromises()

  await fillValidForm(form)
  await form.get('form').trigger('submit')

  await vi.waitFor(() => expect(form.text()).toContain('Guardando tu MIR'))
  form.unmount()
})

it('cancelar emite cancel sin llamar a la API', async () => {
  const form = await mountForm()
  await flushPromises()
  await form.get('[data-testid="cancelar-crear-mir"]').trigger('click')
  expect(form.emitted('cancel')).toBeTruthy()
  expect(createMir).not.toHaveBeenCalled()
  form.unmount()
})

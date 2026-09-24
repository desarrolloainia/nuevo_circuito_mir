import { mountSuspended } from '@nuxt/test-utils/runtime'
import { beforeEach, expect, it, vi } from 'vitest'
import MirDetallePage from './MirDetallePage.vue'

const { getMirByCode, currentUser } = vi.hoisted(() => ({ getMirByCode: vi.fn(), currentUser: { value: { id: 'u-1', rol: 'DETECTOR' } } }))
vi.mock('@/entities/user', async importOriginal => ({ ...await importOriginal(), useCurrentUser: () => currentUser }))
vi.mock('@/entities/mir', async importOriginal => ({ ...await importOriginal(), getMirByCode }))
vi.mock('@/features/revisar-mir', async () => {
  const { defineComponent, h } = await import('vue')
  return {
    RevisarMirPanel: defineComponent({
      props: { mir: { type: Object, required: true } },
      emits: ['revisada'],
      setup: (props, { emit }) => () => h('button', { 'data-testid': 'panel-revision', 'onClick': () => emit('revisada', { ...props.mir, estado: 'RECHAZADA' }) }, 'Panel')
    })
  }
})

beforeEach(() => {
  currentUser.value = { id: 'u-1', rol: 'DETECTOR' }
  getMirByCode.mockReset()
  getMirByCode.mockResolvedValue({
    codigo_mir: '26001', detectada_por_id: 'u-1', descripcion: 'Fuga de aceite ficticia.',
    tipo: 'Incidencia', estado: 'EN_REVISION', fecha_deteccion: '2026-09-20',
    creado_en: '2026-09-21T09:00:00Z', empresa_nombre: 'Empresa Ficticia',
    persona_contacto: 'Persona Ficticia', telefono: '0600123456',
    correo_electronico: 'contacto@ejemplo.test', documento_ids: ['doc-1'],
    solucionado: false
  })
})

it('carga el código solicitado y muestra detección, cliente, estado y número de adjuntos', async () => {
  const page = await mountSuspended(MirDetallePage, { props: { codigoMir: '26001' } })
  await vi.waitFor(() => expect(page.text()).toContain('Fuga de aceite ficticia.'))
  expect(getMirByCode).toHaveBeenCalledWith('26001')
  expect(page.text()).toContain('26001')
  expect(page.text()).toContain('En revisión')
  expect(page.text()).toContain('Empresa Ficticia')
  expect(page.text()).toContain('1 archivo adjunto')
  expect(page.get('a[href="/detector/mis-mir"]').exists()).toBe(true)
  page.unmount()
})

it('no presenta una MIR de otro detector en la vista personal', async () => {
  getMirByCode.mockResolvedValueOnce({ codigo_mir: '26001', detectada_por_id: 'u-2' })
  const page = await mountSuspended(MirDetallePage, { props: { codigoMir: '26001' } })
  await vi.waitFor(() => expect(page.get('[role="alert"]').text()).toContain('No encontramos esta MIR'))
  page.unmount()
})

it('muestra los datos de resolución de una MIR solucionada', async () => {
  getMirByCode.mockResolvedValueOnce({
    codigo_mir: '26001', detectada_por_id: 'u-1', tipo: 'Mejora', estado: 'EN_REVISION',
    descripcion: 'Mejora ficticia.', creado_en: '2026-09-21T09:00:00Z',
    documento_ids: [], solucionado: true, solucion_adoptada: 'Reparación ficticia',
    analisis_causas: 'Desgaste ficticio', algo_mas_que_hacer: 'Revisar otras líneas'
  })
  const page = await mountSuspended(MirDetallePage, { props: { codigoMir: '26001' } })
  await vi.waitFor(() => expect(page.text()).toContain('Reparación ficticia'))
  expect(page.text()).toContain('Desgaste ficticio')
  expect(page.text()).toContain('Revisar otras líneas')
  page.unmount()
})

it('permite reintentar si falla la consulta', async () => {
  getMirByCode.mockRejectedValueOnce(new Error('Error de red'))
  const page = await mountSuspended(MirDetallePage, { props: { codigoMir: '26001' } })
  await vi.waitFor(() => expect(page.get('[role="alert"]').text()).toContain('No pudimos cargar'))
  await page.get('[data-testid="reintentar-detalle-mir"]').trigger('click')
  await vi.waitFor(() => expect(page.text()).toContain('Fuga de aceite ficticia.'))
  page.unmount()
})

it('deja al jefe de calidad revisar una MIR de cualquier detector y volver a su bandeja', async () => {
  currentUser.value = { id: 'j-1', rol: 'JEFE_CLD' }
  const page = await mountSuspended(MirDetallePage, { props: { codigoMir: '26001' } })
  await vi.waitFor(() => expect(page.text()).toContain('Fuga de aceite ficticia.'))
  expect(page.get('a[href="/jefe-calidad/revision-mir"]').exists()).toBe(true)
  page.unmount()
})

it('muestra al jefe de calidad la columna de revisión de una MIR en revisión y refleja su decisión', async () => {
  currentUser.value = { id: 'j-1', rol: 'JEFE_CLD' }
  const page = await mountSuspended(MirDetallePage, { props: { codigoMir: '26001' } })
  await vi.waitFor(() => expect(page.find('aside[aria-label="Revisión"]').exists()).toBe(true))
  await page.get('[data-testid="panel-revision"]').trigger('click')
  await vi.waitFor(() => expect(page.text()).toContain('Rechazada'))
  expect(page.find('aside[aria-label="Revisión"]').exists()).toBe(true)
  page.unmount()
})

it('no ofrece la revisión al detector ni en MIR que ya no están en revisión', async () => {
  const detector = await mountSuspended(MirDetallePage, { props: { codigoMir: '26001' } })
  await vi.waitFor(() => expect(detector.text()).toContain('Fuga de aceite ficticia.'))
  expect(detector.find('aside[aria-label="Revisión"]').exists()).toBe(false)
  detector.unmount()

  currentUser.value = { id: 'j-1', rol: 'JEFE_CLD' }
  getMirByCode.mockResolvedValueOnce({ codigo_mir: '26001', detectada_por_id: 'u-1', estado: 'EN_PROGRESO', tipo: 'Mejora', descripcion: 'Mejora ficticia.', creado_en: '2026-09-21T09:00:00Z', documento_ids: [], solucionado: false })
  const jefe = await mountSuspended(MirDetallePage, { props: { codigoMir: '26001' } })
  await vi.waitFor(() => expect(jefe.text()).toContain('Mejora ficticia.'))
  expect(jefe.find('aside[aria-label="Revisión"]').exists()).toBe(false)
  jefe.unmount()
})

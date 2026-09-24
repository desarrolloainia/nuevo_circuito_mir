import { beforeEach, expect, it, vi } from 'vitest'
import { createMir } from './create-mir'
import type { CreateMirFormState } from '../model/create-mir-form'

const { apiPost } = vi.hoisted(() => ({ apiPost: vi.fn() }))
vi.mock('@/shared/api', () => ({ apiPost }))

const state: CreateMirFormState = {
  nombre: 'Ana Auditora',
  tipo: 'Incidencia',
  usuarioId: 'u-1',
  fechaDeteccion: '2026-01-10',
  detectadoPorId: 'u-2',
  descripcion: 'Fuga detectada en línea 3.',
  solucionada: false,
  solucionAdoptada: '',
  analisisCausas: '',
  algoMasQueHacer: '',
  empresaNombre: 'Ainia',
  personaContacto: 'Marta Cliente',
  telefono: '600123456',
  correoElectronico: 'marta@cliente.es',
  nombreComercial: 'Luis Comercial',
  codigoCliente: 'CL-001',
  archivos: [new File(['contenido'], 'evidencia.jpg')]
}

beforeEach(() => vi.clearAllMocks())

it('envía datos JSON y archivos emparejados en multipart y devuelve el MIR del servidor', async () => {
  const created = { id: 'mir-1', codigo_mir: '26001', estado: 'EN_REVISION' }
  apiPost.mockResolvedValue(created)

  await expect(createMir(state)).resolves.toBe(created)
  expect(apiPost).toHaveBeenCalledWith('/mir', expect.any(FormData))
  const body = apiPost.mock.calls[0]![1] as FormData
  expect(JSON.parse(body.get('datos') as string)).toEqual({
    tipo: 'Incidencia', descripcion: 'Fuga detectada en línea 3.', fecha_deteccion: '2026-01-10',
    detectada_por_id: 'u-2', solucionado: false, empresa_nombre: 'Ainia',
    persona_contacto: 'Marta Cliente', telefono: '600123456', correo_electronico: 'marta@cliente.es',
    nombre_comercial: 'Luis Comercial', codigo_cliente: 'CL-001', tipos_documento: ['imagen']
  })
  expect((body.getAll('archivos')[0] as File).name).toBe('evidencia.jpg')
})

it('envía los tres campos obligatorios al marcar la MIR como solucionada', async () => {
  apiPost.mockResolvedValue({ codigo_mir: '26002' })
  await createMir({ ...state, solucionada: true, solucionAdoptada: ' Reparación ', analisisCausas: ' Desgaste ', algoMasQueHacer: ' Revisar otras líneas ', archivos: [] })
  const body = apiPost.mock.calls[0]![1] as FormData
  expect(JSON.parse(body.get('datos') as string)).toMatchObject({
    solucionado: true, solucion_adoptada: 'Reparación', analisis_causas: 'Desgaste',
    algo_mas_que_hacer: 'Revisar otras líneas', tipos_documento: []
  })
  expect(body.getAll('archivos')).toEqual([])
})

it('propaga el fallo del servidor sin confirmar el alta', async () => {
  apiPost.mockRejectedValue(new Error('422'))
  await expect(createMir(state)).rejects.toThrow('422')
})

it('clasifica cada documento de un envío múltiple en el mismo orden', async () => {
  apiPost.mockResolvedValue({ codigo_mir: '26003' })
  const archivos = ['contrato.PDF', 'acta.docx', 'tabla.xlsx', 'sin-formato.bin'].map(name => new File(['archivo'], name))
  await createMir({ ...state, archivos })
  const body = apiPost.mock.calls[0]![1] as FormData
  expect(JSON.parse(body.get('datos') as string).tipos_documento).toEqual(['pdf', 'word', 'excel', 'otro'])
  expect(body.getAll('archivos')).toHaveLength(4)
})

import { apiPost } from '@/shared/api'
import type { components } from '@/shared/schema'
import type { CreateMirFormState } from '../model/create-mir-form'

type CreateMir = components['schemas']['CrearMirDTO']
type MirRecord = components['schemas']['MirDTO']
type TipoDocumento = components['schemas']['TipoDocumento']

function documentType(file: File): TipoDocumento {
  const extension = file.name.split('.').pop()?.toLowerCase()
  if (extension === 'pdf') return 'pdf'
  if (extension === 'doc' || extension === 'docx') return 'word'
  if (extension === 'xls' || extension === 'xlsx') return 'excel'
  if (file.type.startsWith('image/') || ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension ?? '')) return 'imagen'
  return 'otro'
}

export function createMir(state: CreateMirFormState): Promise<MirRecord> {
  if (!state.tipo) throw new Error('Selecciona el tipo de MIR.')

  const datos: CreateMir = {
    tipo: state.tipo,
    descripcion: state.descripcion.trim(),
    fecha_deteccion: state.fechaDeteccion,
    detectada_por_id: state.detectadoPorId,
    solucionado: state.solucionada,
    empresa_nombre: state.empresaNombre.trim(),
    persona_contacto: state.personaContacto.trim(),
    telefono: state.telefono.trim(),
    correo_electronico: state.correoElectronico.trim(),
    nombre_comercial: state.nombreComercial.trim(),
    codigo_cliente: state.codigoCliente.trim(),
    tipos_documento: state.archivos.map(documentType)
  }
  if (state.solucionada) {
    datos.solucion_adoptada = state.solucionAdoptada.trim()
    datos.analisis_causas = state.analisisCausas.trim()
    datos.algo_mas_que_hacer = state.algoMasQueHacer.trim()
  }

  const body = new FormData()
  body.append('datos', JSON.stringify(datos))
  for (const file of state.archivos) body.append('archivos', file)
  return apiPost<MirRecord>('/mir', body)
}

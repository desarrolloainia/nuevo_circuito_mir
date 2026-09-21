import type { CreateMirFormState } from '../model/create-mir-form'

export interface CreatedMir {
  tipo: CreateMirFormState['tipo']
  descripcion: string
  solucionada: boolean
  empresaNombre: string
  personaContacto: string
  telefono: string
  correoElectronico: string
  nombreComercial: string
  codigoCliente: string
  detectadoPorId: string
  archivosCount: number
}

// Mock: sustituir por POST /mir cuando el backend lo exponga.
export function createMir(state: CreateMirFormState): Promise<CreatedMir> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        tipo: state.tipo,
        descripcion: state.descripcion.trim(),
        solucionada: state.solucionada,
        empresaNombre: state.empresaNombre.trim(),
        personaContacto: state.personaContacto.trim(),
        telefono: state.telefono.trim(),
        correoElectronico: state.correoElectronico.trim(),
        nombreComercial: state.nombreComercial.trim(),
        codigoCliente: state.codigoCliente.trim(),
        detectadoPorId: state.detectadoPorId,
        archivosCount: state.archivos.length
      })
    }, 400)
  })
}

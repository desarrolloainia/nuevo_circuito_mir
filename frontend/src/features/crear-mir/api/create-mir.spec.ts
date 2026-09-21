import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { createMir } from './create-mir'
import type { CreateMirFormState } from '../model/create-mir-form'

const state: CreateMirFormState = {
  nombre: 'Ana Auditora',
  tipo: 'Incidencia',
  usuarioId: 'u-1',
  fechaDeteccion: '2026-01-10',
  detectadoPorId: 'u-2',
  descripcion: 'Fuga detectada en línea 3.',
  solucionada: false,
  empresaNombre: 'Ainia',
  personaContacto: 'Marta Cliente',
  telefono: '600123456',
  correoElectronico: 'marta@cliente.es',
  nombreComercial: 'Luis Comercial',
  codigoCliente: 'CL-001',
  archivos: [new File(['contenido'], 'evidencia.jpg')]
}

beforeEach(() => vi.useFakeTimers())
afterEach(() => vi.useRealTimers())

it('resuelve con el MIR creado a partir del estado del formulario', async () => {
  const result = createMir(state)
  await vi.runAllTimersAsync()
  await expect(result).resolves.toMatchObject({
    tipo: 'Incidencia',
    descripcion: 'Fuga detectada en línea 3.',
    solucionada: false,
    empresaNombre: 'Ainia',
    personaContacto: 'Marta Cliente',
    telefono: '600123456',
    correoElectronico: 'marta@cliente.es',
    nombreComercial: 'Luis Comercial',
    codigoCliente: 'CL-001',
    detectadoPorId: 'u-2',
    archivosCount: 1
  })
})

import { expect, it } from 'vitest'
import { validateCreateMir, type CreateMirFormState } from './create-mir-form'

function validState(): CreateMirFormState {
  return {
    nombre: 'Ana Auditora',
    tipo: 'Incidencia',
    usuarioId: 'u-1',
    fechaDeteccion: '2026-01-10',
    detectadoPorId: 'u-1',
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
    archivos: []
  }
}

it('acepta un estado completo sin errores', () => {
  expect(validateCreateMir(validState())).toEqual([])
})

it('exige tipo, fecha, detector, descripción, empresa y datos de contacto', () => {
  const errors = validateCreateMir({
    ...validState(),
    tipo: undefined,
    fechaDeteccion: '',
    detectadoPorId: '',
    descripcion: '  ',
    empresaNombre: '  ',
    personaContacto: '  ',
    telefono: '  ',
    correoElectronico: '  '
  })
  expect(errors.map(error => error.name)).toEqual(
    expect.arrayContaining([
      'tipo', 'fechaDeteccion', 'detectadoPorId', 'descripcion', 'empresaNombre',
      'personaContacto', 'telefono', 'correoElectronico'
    ])
  )
})

it('no exige nombre del comercial ni código cliente', () => {
  const errors = validateCreateMir({ ...validState(), nombreComercial: '', codigoCliente: '' })
  expect(errors).toEqual([])
})

it('rechaza una fecha de detección futura', () => {
  const errors = validateCreateMir({ ...validState(), fechaDeteccion: '2099-01-01' })
  expect(errors).toEqual([{ name: 'fechaDeteccion', message: 'La fecha de detección no puede ser futura.' }])
})

it('exige los tres datos de solución solo cuando la MIR se marca como solucionada', () => {
  expect(validateCreateMir({ ...validState(), solucionada: true }).map(error => error.name)).toEqual([
    'solucionAdoptada', 'analisisCausas', 'algoMasQueHacer'
  ])
  expect(validateCreateMir({ ...validState(), solucionada: true, solucionAdoptada: 'Reparada', analisisCausas: 'Desgaste', algoMasQueHacer: 'Revisar' })).toEqual([])
})

it('limita los adjuntos a diez', () => {
  const archivos = Array.from({ length: 11 }, (_, i) => new File(['a'], `evidencia-${i}.pdf`))
  expect(validateCreateMir({ ...validState(), archivos }).map(error => error.name)).toContain('archivos')
})

it('comprueba formato del correo y longitudes exigidas por el backend', () => {
  const errors = validateCreateMir({
    ...validState(), correoElectronico: 'incorrecto', telefono: '1'.repeat(51),
    empresaNombre: 'E'.repeat(256), personaContacto: 'P'.repeat(256)
  })
  expect(errors.map(error => error.name)).toEqual(expect.arrayContaining(['correoElectronico', 'telefono', 'empresaNombre', 'personaContacto']))
})

import { expect, it } from 'vitest'
import { loginError, validateEmail, validateRegistration } from './login'

it('valida el correo antes de consultar', () => {
  expect(validateEmail({ email: '' })).toHaveLength(1)
  expect(validateEmail({ email: 'incorrecto' })).toHaveLength(1)
  expect(validateEmail({ email: ' auditor@mir.es ' })).toEqual([])
})

it('traduce los errores HTTP sin mostrar detalles del servidor', () => {
  expect(loginError({ statusCode: 404 })).toContain('No encontramos')
  expect(loginError({ statusCode: 422 })).toContain('correo válido')
  expect(loginError({ statusCode: 409 })).toContain('ya está registrado')
  expect(loginError(new Error('privado'))).toContain('No pudimos conectar')
})

it('exige nombre y departamento para el registro', () => {
  expect(validateRegistration({ email: 'nuevo@mir.es', nombre: '', role: 'DETECTOR', department: ' ' })).toEqual([
    { name: 'nombre', message: 'Introduce tu nombre.' },
    { name: 'department', message: 'Introduce tu departamento.' }
  ])
  expect(validateRegistration({ email: 'nuevo@mir.es', nombre: 'Ada Lovelace', role: 'DETECTOR', department: 'Calidad' })).toEqual([])
})

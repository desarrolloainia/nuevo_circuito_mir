import { expect, it } from 'vitest'
import { homeForRol } from './home'

it('lleva a cada rol a la pantalla de su grupo de rutas', () => {
  expect(homeForRol('DETECTOR')).toBe('/detector/mis-mir')
  expect(homeForRol('JEFE_CLD')).toBe('/jefe-calidad/revision-mir')
})

it('lleva a los roles sin pantalla a la página en construcción', () => {
  expect(homeForRol('EJECUTOR')).toBe('/en-construccion')
  expect(homeForRol(undefined)).toBe('/en-construccion')
})

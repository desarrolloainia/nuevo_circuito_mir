import { mountSuspended } from '@nuxt/test-utils/runtime'
import { expect, it } from 'vitest'
import MirEstadoBadge from './MirEstadoBadge.vue'

it('muestra la etiqueta en español correspondiente al estado', async () => {
  const badge = await mountSuspended(MirEstadoBadge, { props: { estado: 'EN_REVISION' } })
  expect(badge.text()).toBe('En revisión')
})

it('usa el color semántico de éxito para una MIR terminada', async () => {
  const badge = await mountSuspended(MirEstadoBadge, { props: { estado: 'TERMINADA' } })
  expect(badge.findComponent({ name: 'UBadge' }).props('color')).toBe('success')
})

it('usa el color semántico de error para una MIR rechazada', async () => {
  const badge = await mountSuspended(MirEstadoBadge, { props: { estado: 'RECHAZADA' } })
  expect(badge.findComponent({ name: 'UBadge' }).props('color')).toBe('error')
})

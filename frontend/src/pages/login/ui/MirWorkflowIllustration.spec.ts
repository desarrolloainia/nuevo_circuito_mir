import { mountSuspended } from '@nuxt/test-utils/runtime'
import { expect, it } from 'vitest'
import MirWorkflowIllustration from './MirWorkflowIllustration.vue'

it('presenta las etapas en orden y explica las evidencias', async () => {
  const diagram = await mountSuspended(MirWorkflowIllustration)
  expect(diagram.findAll('ol > li').map(step => step.find('h3').text())).toEqual(['Detección', 'Revisión', 'Asignación', 'Resolución', 'Cierre'])
  expect(diagram.text()).toContain('Evidencias')
  diagram.unmount()
})

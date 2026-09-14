import { mountSuspended } from '@nuxt/test-utils/runtime'
import { expect, it } from 'vitest'
import ConstructionPage from './ConstructionPage.vue'

it('explica que la aplicación está en construcción y permite volver al acceso', async () => {
  const page = await mountSuspended(ConstructionPage)
  expect(page.text()).toContain('Todo está en construcción')
  expect(page.find('a[href="/login"]').exists()).toBe(true)
  page.unmount()
})

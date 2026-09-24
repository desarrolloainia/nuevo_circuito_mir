// @ts-check
import withNuxt from './.nuxt/eslint.config.mjs'

export default withNuxt(
  { ignores: ['.agents/**', '.impeccable/**', 'src/shared/schema.ts'] }
)

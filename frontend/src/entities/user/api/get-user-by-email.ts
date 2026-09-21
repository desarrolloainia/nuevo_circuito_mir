import { apiGet } from '@/shared/api'
import type { User } from '../model/types'

export function getUserByEmail(email: string): Promise<User> {
  return apiGet(`/usuarios/${encodeURIComponent(email)}`)
}

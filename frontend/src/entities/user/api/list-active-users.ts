import { apiGet } from '@/shared/api'
import type { User } from '../model/types'

export function listActiveUsers(): Promise<User[]> {
  return apiGet('/usuarios')
}

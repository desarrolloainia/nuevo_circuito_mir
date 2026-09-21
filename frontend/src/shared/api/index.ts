import { useRuntimeConfig } from '#imports'

export function apiGet<T>(path: string): Promise<T> {
  return $fetch<T>(path, { baseURL: useRuntimeConfig().public.apiBase, retry: 0, timeout: 15000 }) as Promise<T>
}

export function apiPost<T>(path: string, body: Record<string, unknown>): Promise<T> {
  return $fetch<T>(path, { method: 'POST', body, baseURL: useRuntimeConfig().public.apiBase, retry: 0, timeout: 15000 }) as Promise<T>
}

export function apiPatch<T>(path: string, body: Record<string, unknown>): Promise<T> {
  return $fetch<T>(path, { method: 'PATCH', body, baseURL: useRuntimeConfig().public.apiBase, retry: 0, timeout: 15000 }) as Promise<T>
}

export function apiDelete<T>(path: string): Promise<T> {
  return $fetch<T>(path, { method: 'DELETE', baseURL: useRuntimeConfig().public.apiBase, retry: 0, timeout: 15000 }) as Promise<T>
}

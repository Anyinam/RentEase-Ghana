import type { PropertySearchResponse } from '../types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:5000/api'

export async function searchProperties(params: URLSearchParams, signal?: AbortSignal): Promise<PropertySearchResponse> {
  const response = await fetch(`${API_URL}/properties?${params.toString()}`, { signal })
  if (!response.ok) throw new Error('Unable to load properties. Please try again.')
  return response.json() as Promise<PropertySearchResponse>
}

export function getApiUrl(): string {
  return API_URL
}

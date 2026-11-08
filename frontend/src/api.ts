import type { Health, Prediction } from './types'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function readError(response: Response) {
  try {
    const body = await response.json()
    return body.detail || 'Request failed.'
  } catch {
    return 'Request failed. Check that the backend is running.'
  }
}

export async function getHealth(): Promise<Health> {
  const response = await fetch(`${API}/api/health`)
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

export async function getDemo(): Promise<Prediction> {
  const response = await fetch(`${API}/api/demo`)
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

export async function predictFile(file: File): Promise<Prediction> {
  const form = new FormData()
  form.append('file', file)
  const response = await fetch(`${API}/api/predict`, { method: 'POST', body: form })
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

export async function getMetrics() {
  const response = await fetch(`${API}/api/model/metrics`)
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

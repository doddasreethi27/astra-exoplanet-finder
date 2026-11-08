export type Evidence = { title: string; detail: string; status: 'supporting' | 'caution' | 'neutral' }
export type Point = { time: number; flux: number }
export type Prediction = {
  target_name: string
  category: string
  confidence: number
  model_name: string
  mode: 'trained_model' | 'demo'
  summary: string
  features: Record<string, number>
  evidence: Evidence[]
  points: Point[]
  disclaimer: string
}
export type Health = { status: string; model_loaded: boolean; model_name: string; cnn_available: boolean }

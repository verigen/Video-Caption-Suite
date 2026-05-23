import type { VideoInfo, CaptionInfo } from './video'
import type { Settings } from './settings'
import type { ProgressState } from './progress'

export interface ApiResponse<T> {
  data: T | null
  error: string | null
}

export interface VideoListResponse {
  videos: VideoInfo[]
  total_count: number
}

export interface CaptionListResponse {
  captions: CaptionInfo[]
  total_count: number
}

export interface ProcessingRequest {
  video_names?: string[]
}

export interface ProcessingResponse {
  success: boolean
  message: string
  videos_queued: number
}

export interface ModelStatus {
  loaded: boolean
  model_id: string | null
  api_base_url: string | null
  available_models: string[]
}

export interface HealthResponse {
  status: string
  model_loaded: boolean
  processing: boolean
}

// Re-export for convenience
export type { Settings, ProgressState, VideoInfo, CaptionInfo }

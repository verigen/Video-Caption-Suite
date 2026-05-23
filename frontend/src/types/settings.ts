export interface Settings {
  api_base_url: string
  api_key: string
  api_model_name: string
  max_frames: number
  frame_size: number
  max_tokens: number
  temperature: number
  include_metadata: boolean
  prompt: string
}

export interface SettingsUpdate {
  api_base_url?: string
  api_key?: string
  api_model_name?: string
  max_frames?: number
  frame_size?: number
  max_tokens?: number
  temperature?: number
  include_metadata?: boolean
  prompt?: string
}

export const defaultSettings: Settings = {
  api_base_url: 'http://localhost:8080',
  api_key: '',
  api_model_name: '',
  max_frames: 16,
  frame_size: 336,
  max_tokens: 512,
  temperature: 0.3,
  include_metadata: false,
  prompt: `Describe this video in detail. Include:
- The main subject and their actions
- The setting and environment
- Any notable objects or elements
- The overall mood or atmosphere
- Any text visible in the video`,
}

// Server model discovery from GET /api/server/models
export interface ServerModelsResponse {
  models: string[]
  api_base_url: string
}

// Prompt Library types
export interface SavedPrompt {
  id: string
  name: string
  prompt: string
  created_at: string
}

export interface PromptLibrary {
  prompts: SavedPrompt[]
}

export interface CreatePromptRequest {
  name: string
  prompt: string
}

export interface UpdatePromptRequest {
  name?: string
  prompt?: string
}

// Directory types
export interface DirectoryRequest {
  directory: string
  traverse_subfolders?: boolean
  include_videos?: boolean
  include_images?: boolean
}

export interface DirectoryResponse {
  directory: string
  video_count?: number
  image_count?: number
  traverse_subfolders?: boolean
  include_videos?: boolean
  include_images?: boolean
}

export interface DirectoryBrowseResponse {
  current: string
  parent: string | null
  directories: { name: string; path: string }[]
}

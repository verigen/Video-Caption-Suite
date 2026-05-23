import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useSettingsStore } from '../settingsStore'

// Mock fetch
(globalThis as any).fetch = vi.fn()

describe('settingsStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initializes with default settings', () => {
    const store = useSettingsStore()

    expect(store.settings.api_base_url).toBe('http://localhost:8080')
    expect(store.settings.api_model_name).toBe('')
    expect(store.settings.max_frames).toBe(16)
    expect(store.settings.temperature).toBe(0.3)
  })

  it('computes hasChanges correctly', () => {
    const store = useSettingsStore()

    // Initially no changes
    expect(store.hasChanges).toBe(false)

    // Make a change
    store.settings.max_frames = 8
    expect(store.hasChanges).toBe(true)
  })

  it('setLocalSetting updates single setting', () => {
    const store = useSettingsStore()

    store.setLocalSetting('max_frames', 32)
    expect(store.settings.max_frames).toBe(32)

    store.setLocalSetting('temperature', 0.7)
    expect(store.settings.temperature).toBe(0.7)

    store.setLocalSetting('api_model_name', 'qwen2.5-vl-7b')
    expect(store.settings.api_model_name).toBe('qwen2.5-vl-7b')
  })

  it('fetchSettings makes API call', async () => {
    const mockSettings = {
      api_base_url: 'http://localhost:8080',
      api_key: '',
      api_model_name: 'qwen2.5-vl-7b',
      max_frames: 8,
      frame_size: 224,
      max_tokens: 256,
      temperature: 0.5,
      include_metadata: true,
      prompt: 'Test prompt',
    }

    ;((globalThis as any).fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockSettings),
    })

    const store = useSettingsStore()
    await store.fetchSettings()

    expect((globalThis as any).fetch).toHaveBeenCalledWith('/api/settings')
    expect(store.settings.api_model_name).toBe('qwen2.5-vl-7b')
    expect(store.settings.max_frames).toBe(8)
  })

  it('fetchSettings handles errors', async () => {
    ;((globalThis as any).fetch as any).mockResolvedValueOnce({
      ok: false,
    })

    const store = useSettingsStore()
    await store.fetchSettings()

    expect(store.error).toBe('Failed to fetch settings')
  })

  it('updateSettings makes POST request', async () => {
    const mockResponse = {
      api_model_name: 'qwen2.5-vl-7b',
      max_frames: 32,
    }

    ;((globalThis as any).fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    })

    const store = useSettingsStore()
    await store.updateSettings({ max_frames: 32 })

    expect((globalThis as any).fetch).toHaveBeenCalledWith('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ max_frames: 32 }),
    })
  })

  it('resetSettings makes POST to reset endpoint', async () => {
    const defaultSettingsResponse = {
      api_base_url: 'http://localhost:8080',
      api_key: '',
      api_model_name: '',
      max_frames: 16,
      frame_size: 336,
      max_tokens: 512,
      temperature: 0.3,
      include_metadata: false,
      prompt: 'Default prompt',
    }

    ;((globalThis as any).fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(defaultSettingsResponse),
    })

    const store = useSettingsStore()

    // First change something
    store.settings.max_frames = 8

    // Then reset
    await store.resetSettings()

    expect((globalThis as any).fetch).toHaveBeenCalledWith('/api/settings/reset', {
      method: 'POST',
    })
    expect(store.settings.max_frames).toBe(16)
  })

  it('loading state is managed correctly', async () => {
    ;((globalThis as any).fetch as any).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({
        ok: true,
        json: () => Promise.resolve({}),
      }), 100))
    )

    const store = useSettingsStore()

    expect(store.loading).toBe(false)

    const promise = store.fetchSettings()
    expect(store.loading).toBe(true)

    await promise
    expect(store.loading).toBe(false)
  })
})

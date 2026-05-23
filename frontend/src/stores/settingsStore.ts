import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Settings, SettingsUpdate } from '@/types'
import { defaultSettings } from '@/types'

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<Settings>({ ...defaultSettings })
  const loading = ref(false)
  const error = ref<string | null>(null)

  const hasChanges = computed(() => {
    return JSON.stringify(settings.value) !== JSON.stringify(defaultSettings)
  })

  async function fetchSettings() {
    loading.value = true
    error.value = null

    try {
      const response = await fetch('/api/settings')
      if (!response.ok) throw new Error('Failed to fetch settings')
      settings.value = await response.json()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  async function updateSettings(update: SettingsUpdate) {
    loading.value = true
    error.value = null

    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(update),
      })
      if (!response.ok) throw new Error('Failed to update settings')
      settings.value = await response.json()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Unknown error'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function resetSettings() {
    loading.value = true
    error.value = null

    try {
      const response = await fetch('/api/settings/reset', { method: 'POST' })
      if (!response.ok) throw new Error('Failed to reset settings')
      settings.value = await response.json()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Unknown error'
      throw e
    } finally {
      loading.value = false
    }
  }

  function setLocalSetting<K extends keyof Settings>(key: K, value: Settings[K]) {
    settings.value[key] = value
  }

  return {
    settings,
    loading,
    error,
    hasChanges,
    fetchSettings,
    updateSettings,
    resetSettings,
    setLocalSetting,
  }
})

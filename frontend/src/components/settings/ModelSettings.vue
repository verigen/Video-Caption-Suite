<script setup lang="ts">
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useSettingsStore } from '@/stores/settingsStore'
import { BaseInput, BaseSelect } from '@/components/base'

const settingsStore = useSettingsStore()
const { settings } = storeToRefs(settingsStore)

const availableModels = ref<string[]>([])
const discovering = ref(false)
const discoverError = ref<string | null>(null)

const modelOptions = ref<{ value: string; label: string }[]>([])

async function discoverModels() {
  discovering.value = true
  discoverError.value = null
  availableModels.value = []
  modelOptions.value = []

  // Save the current URL/key first so the backend uses what's currently typed
  await settingsStore.updateSettings({
    api_base_url: settings.value.api_base_url,
    api_key: settings.value.api_key,
  })

  try {
    const response = await fetch('/api/server/models')
    if (!response.ok) {
      const data = await response.json().catch(() => ({}))
      throw new Error(data.detail || `Server returned ${response.status}`)
    }
    const data = await response.json()
    availableModels.value = data.models ?? []
    modelOptions.value = availableModels.value.map(m => ({ value: m, label: m }))

    if (availableModels.value.length === 1 && !settings.value.api_model_name) {
      settingsStore.setLocalSetting('api_model_name', availableModels.value[0])
    }
  } catch (e) {
    discoverError.value = e instanceof Error ? e.message : 'Failed to reach server'
  } finally {
    discovering.value = false
  }
}

function updateApiBaseUrl(value: string | number) {
  settingsStore.setLocalSetting('api_base_url', String(value))
}

function updateApiKey(value: string | number) {
  settingsStore.setLocalSetting('api_key', String(value))
}

function updateApiModelName(value: string) {
  settingsStore.setLocalSetting('api_model_name', value)
}

function updateApiModelNameInput(value: string | number) {
  settingsStore.setLocalSetting('api_model_name', String(value))
}
</script>

<template>
  <div class="space-y-4">
    <BaseInput
      :model-value="settings.api_base_url"
      label="API Server URL"
      placeholder="http://localhost:8080"
      hint="Base URL of your llama.cpp (or other OpenAI-compatible) server"
      @update:model-value="updateApiBaseUrl"
    />

    <BaseInput
      :model-value="settings.api_key"
      label="API Key"
      placeholder="(leave empty for local servers)"
      hint="Optional — most local servers don't require a key"
      @update:model-value="updateApiKey"
    />

    <!-- Model selection: dropdown if models discovered, text input otherwise -->
    <div class="space-y-2">
      <div class="flex items-end gap-2">
        <div class="flex-1">
          <BaseSelect
            v-if="modelOptions.length > 0"
            :model-value="settings.api_model_name"
            :options="modelOptions"
            label="Model"
            hint="Select a model from your server"
            @update:model-value="updateApiModelName"
          />
          <BaseInput
            v-else
            :model-value="settings.api_model_name"
            label="Model Name"
            placeholder="e.g. qwen2.5-vl-7b"
            hint="Name as reported by the server. Click Refresh to discover."
            @update:model-value="updateApiModelNameInput"
          />
        </div>

        <button
          class="mb-[1px] px-3 py-2 text-sm rounded-lg bg-dark-700 hover:bg-dark-600 text-dark-200 border border-dark-600 transition-colors disabled:opacity-50 whitespace-nowrap"
          :disabled="discovering"
          @click="discoverModels"
        >
          {{ discovering ? 'Checking…' : 'Refresh' }}
        </button>
      </div>

      <p v-if="discoverError" class="text-xs text-red-400">
        {{ discoverError }}
      </p>
      <p v-else-if="availableModels.length > 0" class="text-xs text-dark-400">
        {{ availableModels.length }} model{{ availableModels.length !== 1 ? 's' : '' }} available on server
      </p>
    </div>
  </div>
</template>

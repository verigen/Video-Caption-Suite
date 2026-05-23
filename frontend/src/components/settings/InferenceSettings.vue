<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useSettingsStore } from '@/stores/settingsStore'
import { BaseSlider, BaseToggle } from '@/components/base'

const settingsStore = useSettingsStore()
const { settings } = storeToRefs(settingsStore)

function updateMaxFrames(value: number) {
  settingsStore.setLocalSetting('max_frames', value)
}

function updateFrameSize(value: number) {
  settingsStore.setLocalSetting('frame_size', value)
}

function updateMaxTokens(value: number) {
  settingsStore.setLocalSetting('max_tokens', value)
}

function updateTemperature(value: number) {
  settingsStore.setLocalSetting('temperature', value)
}

function updateIncludeMetadata(value: boolean) {
  settingsStore.setLocalSetting('include_metadata', value)
}
</script>

<template>
  <div class="space-y-6">
    <BaseSlider
      :model-value="settings.max_frames"
      label="Max Frames"
      :min="1"
      :max="128"
      :step="1"
      @update:model-value="updateMaxFrames"
    />

    <BaseSlider
      :model-value="settings.frame_size"
      label="Frame Size"
      :min="224"
      :max="672"
      :step="56"
      :format-value="(v: number) => `${v}px`"
      @update:model-value="updateFrameSize"
    />

    <BaseSlider
      :model-value="settings.max_tokens"
      label="Max Tokens"
      :min="64"
      :max="2048"
      :step="64"
      @update:model-value="updateMaxTokens"
    />

    <BaseSlider
      :model-value="settings.temperature"
      label="Temperature"
      :min="0"
      :max="2"
      :step="0.1"
      :format-value="(v: number) => v.toFixed(1)"
      @update:model-value="updateTemperature"
    />

    <div class="pt-4 space-y-4">
      <h4 class="text-xs font-medium text-dark-400 uppercase tracking-wider">Output</h4>

      <BaseToggle
        :model-value="settings.include_metadata"
        label="Include Metadata"
        description="Add timing and token info to caption files"
        @update:model-value="updateIncludeMetadata"
      />
    </div>
  </div>
</template>

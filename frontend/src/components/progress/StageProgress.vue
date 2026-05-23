<script setup lang="ts">
import { computed } from 'vue'
import type { ProcessingStage, ProcessingSubstage } from '@/types'

interface Props {
  stage: ProcessingStage
  substage: ProcessingSubstage
  modelLoaded: boolean
}

const props = defineProps<Props>()

interface StageInfo {
  key: string
  label: string
  isComplete: boolean
  isActive: boolean
}

const stages = computed<StageInfo[]>(() => {
  const currentStage = props.stage

  return [
    {
      key: 'model',
      label: 'Model Ready',
      isComplete: props.modelLoaded,
      isActive: currentStage === 'loading_model',
    },
    {
      key: 'extract',
      label: 'Extract Frames',
      isComplete: currentStage === 'complete' || (currentStage === 'processing' && props.substage !== 'extracting_frames' && props.substage !== 'idle'),
      isActive: currentStage === 'processing' && props.substage === 'extracting_frames',
    },
    {
      key: 'encode',
      label: 'Encode',
      isComplete: currentStage === 'complete' || (currentStage === 'processing' && props.substage === 'generating'),
      isActive: currentStage === 'processing' && props.substage === 'encoding',
    },
    {
      key: 'generate',
      label: 'Generate',
      isComplete: currentStage === 'complete',
      isActive: currentStage === 'processing' && props.substage === 'generating',
    },
  ]
})
</script>

<template>
  <div class="flex items-center justify-between">
    <template v-for="(stageInfo, index) in stages" :key="stageInfo.key">
      <!-- Stage indicator -->
      <div class="flex flex-col items-center">
        <div
          :class="[
            'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-300',
            stageInfo.isComplete
              ? 'bg-green-500 text-white'
              : stageInfo.isActive
                ? 'bg-primary-500 text-white animate-pulse'
                : 'bg-dark-700 text-dark-400',
          ]"
        >
          <svg
            v-if="stageInfo.isComplete"
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 13l4 4L19 7"
            />
          </svg>
          <span v-else>{{ index + 1 }}</span>
        </div>
        <span
          :class="[
            'mt-2 text-xs font-medium',
            stageInfo.isComplete || stageInfo.isActive
              ? 'text-dark-200'
              : 'text-dark-500',
          ]"
        >
          {{ stageInfo.label }}
        </span>
      </div>

      <!-- Connector line -->
      <div
        v-if="index < stages.length - 1"
        :class="[
          'flex-1 h-0.5 mx-2 transition-colors duration-300',
          stageInfo.isComplete ? 'bg-green-500' : 'bg-dark-700',
        ]"
      />
    </template>
  </div>
</template>

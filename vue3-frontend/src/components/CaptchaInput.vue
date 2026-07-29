<script setup>
import { ref, onMounted } from 'vue'
import { captchaService } from '@/services/captchaService'
import Input from '@/components/ui/Input.vue'
import Label from '@/components/ui/Label.vue'
import { RefreshCw } from 'lucide-vue-next'

const svg = ref('')
const token = ref('')
const answer = ref('')
const isLoading = ref(false)

async function loadCaptcha() {
  isLoading.value = true
  try {
    const { data: res } = await captchaService.generate()
    token.value = res.token
    svg.value = res.svg
    answer.value = ''
  } catch {
    svg.value = ''
    token.value = ''
  } finally {
    isLoading.value = false
  }
}

onMounted(loadCaptcha)

defineExpose({ token, answer })
</script>

<template>
  <div class="space-y-2">
    <Label>CAPTCHA Verification</Label>
    <div class="flex items-center gap-2">
      <div v-if="svg" class="rounded-lg border bg-white p-1" v-html="svg" />
      <div v-else class="h-[50px] w-[160px] rounded-lg border bg-muted flex items-center justify-center text-xs text-muted-foreground">
        {{ isLoading ? 'Loading...' : 'Failed to load' }}
      </div>
      <button type="button" @click="loadCaptcha" class="p-2 rounded-md hover:bg-muted transition-colors shrink-0" title="Refresh CAPTCHA">
        <RefreshCw class="h-4 w-4" :class="{ 'animate-spin': isLoading }" />
      </button>
    </div>
    <Input v-model="answer" placeholder="Enter the code above" />
  </div>
</template>

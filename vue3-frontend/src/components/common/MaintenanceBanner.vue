<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { AlertCircle, Clock, ShieldAlert } from 'lucide-vue-next'

const props = defineProps()

const timeLeft = ref('')
const isUrgent = ref(false)
let timer = null

function updateCountdown() {
  if (!props.scheduledAt) return
  
  const target = new Date(props.scheduledAt).getTime()
  const now = new Date().getTime()
  const diff = target - now
  
  if (diff <= 0) {
    timeLeft.value = '00:00'
    isUrgent.value = true
    return
  }
  
  const minutes = Math.floor(diff / 60000)
  const seconds = Math.floor((diff % 60000) / 1000)
  
  timeLeft.value = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  
  // Urgent if less than 1 minute
  isUrgent.value = diff < 60000
}

onMounted(() => {
  updateCountdown()
  timer = setInterval(updateCountdown, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div 
    v-if="scheduledAt"
    class="relative overflow-hidden transition-all duration-500"
    :class="[
      isUrgent 
        ? 'bg-destructive text-destructive-foreground animate-pulse' 
        : 'bg-amber-500 text-white'
    ]"
  >
    <!-- Background Decoration -->
    <div class="absolute inset-0 opacity-10 pointer-events-none">
      <ShieldAlert class="absolute -right-4 -top-4 w-24 h-24 rotate-12" />
    </div>

    <div class="max-w-7xl mx-auto px-4 py-2.5 flex items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="hidden sm:flex p-1.5 bg-white/20 rounded-lg">
          <AlertCircle class="w-5 h-5" />
        </div>
        <div class="flex flex-col sm:flex-row sm:items-center sm:gap-2">
          <span class="font-bold text-xs sm:text-sm uppercase tracking-wider">Pemeriharaan Sistem Terjadwal</span>
          <span class="opacity-90 text-[10px] sm:text-xs">Segera simpan pekerjaan Anda sebelum waktu habis!</span>
        </div>
      </div>

      <div class="shrink-0 flex items-center gap-2 px-3 py-1 bg-white/20 rounded-full border border-white/30 backdrop-blur-sm">
        <Clock class="w-4 h-4" />
        <span class="font-mono font-bold text-sm tracking-tighter">{{ timeLeft }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.9; }
  100% { opacity: 1; }
}
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>

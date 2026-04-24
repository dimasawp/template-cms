<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Button from '@/components/ui/Button.vue'
import { ShieldAlert, LogOut } from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-muted p-4">
    <div class="max-w-md w-full bg-card rounded-2xl shadow-xl border border-border p-8 text-center">
      <div class="flex justify-center mb-6">
        <div class="p-4 bg-amber-500/10 rounded-full text-amber-500">
          <ShieldAlert class="w-12 h-12" />
        </div>
      </div>
      
      <h1 class="text-2xl font-bold text-foreground">Sistem Sedang Dalam Pemeliharaan</h1>
      <p class="mt-3 text-muted-foreground leading-relaxed text-sm">
        Kami sedang meningkatkan kualitas layanan kami. Kami akan segera kembali secepat mungkin. Silakan coba lagi nanti.
      </p>

      <div class="mt-8 pt-6 border-t border-border flex flex-col gap-3">
        <Button variant="outline" class="w-full" @click="handleLogout">
          <LogOut class="w-4 h-4 mr-2" />
          Keluar & Kembali ke Login
        </Button>
        <p class="text-[10px] text-muted-foreground italic">
          *Session Anda akan dibersihkan demi keamanan selama pemeliharaan.
        </p>
      </div>
    </div>
  </div>
</template>

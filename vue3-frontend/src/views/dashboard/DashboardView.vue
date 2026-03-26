<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import CardStats from '@/components/ui/CardStats.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import { Users, Shield, Bell, Activity } from 'lucide-vue-next'

const auth = useAuthStore()
</script>

<template>
  <div>
    <PageHeader title="Dashboard" :description="`Selamat datang, ${auth.user?.full_name || auth.username}!`" />

    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <CardStats title="Total Users" value="—" description="placeholder">
        <template #icon><Users class="h-5 w-5 text-muted-foreground" /></template>
      </CardStats>
      <CardStats title="Active Roles" value="—" description="placeholder">
        <template #icon><Shield class="h-5 w-5 text-muted-foreground" /></template>
      </CardStats>
      <CardStats title="Notifications" value="—" description="placeholder">
        <template #icon><Bell class="h-5 w-5 text-muted-foreground" /></template>
      </CardStats>
      <CardStats title="System Status" value="Online" description="All systems normal" trend="up">
        <template #icon><Activity class="h-5 w-5 text-green-500" /></template>
      </CardStats>
    </div>

    <div class="mt-8 rounded-lg border bg-card p-6">
      <h2 class="text-lg font-semibold">Getting Started</h2>
      <p class="mt-2 text-sm text-muted-foreground mb-4">
        Ini adalah template dashboard CMS. Ganti konten halaman ini dengan data dan widget yang relevan untuk project Anda.
        Untuk mempermudah pengembangan, kami telah menyediakan kumpulan komponen UI yang dapat Anda gunakan kembali.
      </p>
      
      <router-link to="/components" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-10 px-4 py-2 bg-primary text-primary-foreground hover:bg-primary/90">
        Lihat Dokumentasi Komponen UI →
      </router-link>
    </div>
  </div>
</template>

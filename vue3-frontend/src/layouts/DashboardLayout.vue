<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import { useSettingsStore } from '@/stores/settings'
import { notificationService } from '@/services/notificationService'
import Toaster from '@/components/ui/Toaster.vue'
import {
  LayoutDashboard, Users, Shield, Bell, Menu, X, LogOut, Sun, Moon, Settings, Monitor, History, ChevronDown
} from 'lucide-vue-next'
import Avatar from '@/components/ui/Avatar.vue'
import { useConfirmation } from '@/composables/useConfirmation'
import { useRealtime } from '@/composables/useRealtime'
import MaintenanceBanner from '@/components/common/MaintenanceBanner.vue'
import ConfirmationDialog from '@/components/ui/ConfirmationDialog.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const settingsStore = useSettingsStore()
const { isDark, toggleTheme } = useTheme()
const confirm = useConfirmation()
const { status: maintenanceStatus } = useRealtime()

const sidebarOpen = ref(true)
const mobileSidebarOpen = ref(false)

const menuItems = computed(() => [
  { name: 'Dashboard', icon: LayoutDashboard, route: '/dashboard' },
  { name: 'Users', icon: Users, route: '/users', permission: 'users.view' },
  { name: 'Roles', icon: Shield, route: '/roles', permission: 'roles.view' },
  { name: 'Global Settings', icon: Settings, route: '/global-settings', permission: 'settings.view' },
  { name: 'Active Sessions', icon: Monitor, route: '/active-sessions', permission: 'sessions.view' },
  { name: 'Audit Trail', icon: History, route: '/settings/audit-logs', permission: 'audit.view' },
])

const visibleMenu = computed(() =>
  menuItems.value.filter(m => !m.permission || auth.hasPermission(m.permission))
)

function isActive(path) {
  return route.path === path
}

async function handleLogout() {
  const ok = await confirm.confirm({
    title: 'Konfirmasi Logout',
    message: 'Apakah Anda yakin ingin keluar dari aplikasi?',
    variant: 'destructive'
  })
  
  if (ok) {
    await auth.logout()
    router.push('/login')
  }
}

const unreadCount = ref(0)

onMounted(async () => {
  // Fetch Notification Badge
  try {
    const { data: res } = await notificationService.badge()
    unreadCount.value = res.data.unread_count
  } catch { /* ignore */ }
})
</script>

<template>
  <div class="flex h-screen overflow-hidden">
    <!-- Sidebar (Desktop) -->
    <aside
      :class="[
        'hidden lg:flex flex-col border-r bg-card transition-all duration-300',
        sidebarOpen ? 'w-64' : 'w-16'
      ]"
    >
      <!-- Brand -->
      <div class="flex h-16 items-center justify-between px-4 border-b">
        <span v-if="sidebarOpen" class="text-lg font-bold text-primary truncate">{{ settingsStore.siteName }}</span>
        <button @click="sidebarOpen = !sidebarOpen" class="p-1 rounded hover:bg-accent">
          <Menu class="h-5 w-5" />
        </button>
      </div>

      <!-- Nav -->
      <nav class="flex-1 overflow-y-auto py-4 px-2 space-y-1">
        <router-link
          v-for="item in visibleMenu"
          :key="item.route"
          :to="item.route"
          :class="[
            'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
            isActive(item.route)
              ? 'bg-primary/10 text-primary'
              : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
          ]"
        >
          <component :is="item.icon" class="h-5 w-5 shrink-0" />
          <span v-if="sidebarOpen">{{ item.name }}</span>
        </router-link>
      </nav>
    </aside>

    <!-- Mobile sidebar overlay -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="mobileSidebarOpen" class="fixed inset-0 z-40 bg-black/50 lg:hidden" @click="mobileSidebarOpen = false" />
      </Transition>
      <Transition name="slide">
        <aside v-if="mobileSidebarOpen" class="fixed inset-y-0 left-0 z-50 w-64 bg-card border-r shadow-xl lg:hidden">
          <div class="flex h-16 items-center justify-between px-4 border-b">
            <span class="text-lg font-bold text-primary truncate">{{ settingsStore.siteName }}</span>
            <button @click="mobileSidebarOpen = false"><X class="h-5 w-5" /></button>
          </div>
          <nav class="py-4 px-2 space-y-1">
            <router-link
              v-for="item in visibleMenu" :key="item.route" :to="item.route"
              :class="[
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium',
                isActive(item.route) ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-accent'
              ]"
              @click="mobileSidebarOpen = false"
            >
              <component :is="item.icon" class="h-5 w-5 shrink-0" />
              {{ item.name }}
            </router-link>
          </nav>
        </aside>
      </Transition>
    </Teleport>

    <!-- Main content -->
    <div class="flex flex-1 flex-col overflow-hidden">
      <!-- Top bar -->
      <header class="flex h-16 items-center justify-between border-b bg-card px-4 lg:px-6">
        <button class="lg:hidden p-1 rounded hover:bg-accent" @click="mobileSidebarOpen = true">
          <Menu class="h-5 w-5" />
        </button>

        <div class="flex-1" />

        <div class="flex items-center gap-2">
          <!-- Theme toggle -->
          <button @click="toggleTheme" class="p-2 rounded-md hover:bg-accent">
            <Sun v-if="isDark" class="h-5 w-5" />
            <Moon v-else class="h-5 w-5" />
          </button>

          <!-- Notification bell -->
          <router-link 
            to="/notifications" 
            class="relative p-2 rounded-md hover:bg-accent text-muted-foreground hover:text-foreground"
            title="Pemberitahuan"
          >
            <Bell class="h-5 w-5" />
            <span 
              v-if="unreadCount > 0" 
              class="absolute top-1.5 right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-destructive text-[10px] font-bold text-white shadow-sm"
            >
              {{ unreadCount > 9 ? '9+' : unreadCount }}
            </span>
          </router-link>

          <!-- User menu -->
          <div class="flex items-center gap-1 ml-2 border-l pl-4">
            <router-link 
              to="/profile" 
              class="flex items-center gap-3 px-2 py-1.5 rounded-lg hover:bg-accent transition-all group"
            >
              <div class="hidden sm:block text-right">
                <p class="text-sm font-bold leading-tight group-hover:text-primary transition-colors">{{ auth.user?.full_name || auth.username }}</p>
                <p class="text-[10px] text-muted-foreground capitalize">{{ auth.userRole }}</p>
              </div>
              <div class="relative shrink-0">
                <Avatar 
                  :src="auth.user?.avatar" 
                  :name="auth.user?.full_name || auth.username" 
                  size="sm" 
                  class="border-2 border-transparent group-hover:border-primary/20 transition-all"
                />
                <div class="absolute -bottom-1 -right-1 bg-background rounded-full p-0.5 border shadow-sm lg:hidden sm:block">
                  <ChevronDown class="h-2 w-2 text-muted-foreground" />
                </div>
              </div>
              <ChevronDown class="hidden lg:block h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
            </router-link>
            
            <button 
              @click="handleLogout" 
              class="p-2 rounded-md hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-colors ml-1" 
              title="Logout"
            >
              <LogOut class="h-4 w-4" />
            </button>
          </div>
        </div>
      </header>

      <!-- Maintenance Alert Banner -->
      <MaintenanceBanner 
        v-if="maintenanceStatus.maintenance_mode === 'true' && maintenanceStatus.maintenance_scheduled_at"
        :scheduled-at="maintenanceStatus.maintenance_scheduled_at" 
      />

      <!-- Page content -->
      <main class="flex flex-1 flex-col overflow-hidden bg-muted/10">
        <div class="flex-1 overflow-y-auto p-4 lg:p-6">
          <router-view />
        </div>
        
        <!-- Footer -->
        <footer class="py-4 ps-4 text-start text-sm text-muted-foreground border-t bg-card/60">
          &copy; {{ new Date().getFullYear() }} {{ settingsStore.siteName }}. Version {{ settingsStore.appVersion }}
        </footer>
      </main>
    </div>
  </div>

  <ConfirmationDialog 
    :open="confirm.isOpen.value"
    :title="confirm.title.value"
    :message="confirm.message.value"
    :variant="confirm.variant.value"
    @confirm="confirm.onConfirm"
    @cancel="confirm.onCancel"
  />
  <Toaster />
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.slide-enter-active, .slide-leave-active { transition: transform 0.3s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(-100%); }
</style>

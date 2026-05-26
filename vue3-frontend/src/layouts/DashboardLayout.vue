<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import { useSettingsStore } from '@/stores/settings'
import { notificationService } from '@/services/notificationService'
import Toaster from '@/components/ui/Toaster.vue'
import {
  LayoutDashboard, Users, Shield, Bell, Menu, X, LogOut, Sun, Moon, Settings, Monitor, History, ChevronDown, FolderTree, FileText
} from 'lucide-vue-next'
import Avatar from '@/components/ui/Avatar.vue'
import { useConfirmation } from '@/composables/useConfirmation'
import { useRealtime } from '@/composables/useRealtime'
import MaintenanceBanner from '@/components/common/MaintenanceBanner.vue'
import ConfirmationDialog from '@/components/ui/ConfirmationDialog.vue'
import Breadcrumbs from '@/components/common/Breadcrumbs.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const settingsStore = useSettingsStore()
const { isDark, toggleTheme } = useTheme()
const confirm = useConfirmation()
const { status: maintenanceStatus } = useRealtime()

const sidebarOpen = ref(true)
const mobileSidebarOpen = ref(false)

const openGroups = ref(['Konten Web', 'Pengaturan'])

const toggleGroup = (groupName) => {
  if (openGroups.value.includes(groupName)) {
    openGroups.value = openGroups.value.filter(g => g !== groupName)
  } else {
    openGroups.value.push(groupName)
  }
}

const menuGroups = computed(() => [
  {
    name: null, // No label for the first group
    items: [
      { name: 'Dashboard', icon: LayoutDashboard, route: '/dashboard' }
    ]
  },
  {
    name: 'Konten Web',
    items: [
      { name: 'Postingan', icon: FileText, route: '/posts', permission: 'posts.view' },
      { name: 'Kategori', icon: FolderTree, route: '/categories', permission: 'categories.view' }
    ]
  },
  {
    name: 'Pengaturan',
    items: [
      { name: 'User Management', icon: Users, route: '/users', permission: 'users.view' },
      { name: 'Role & Permission', icon: Shield, route: '/roles', permission: 'roles.view' },
      { name: 'Global Settings', icon: Settings, route: '/global-settings', permission: 'settings.view' },
      { name: 'Active Sessions', icon: Monitor, route: '/active-sessions', permission: 'sessions.view' },
      { name: 'Audit Logs', icon: History, route: '/settings/audit-logs', permission: 'audit.view' },
    ]
  }
])

const visibleGroups = computed(() => {
  return menuGroups.value.map(group => ({
    ...group,
    items: group.items.filter(m => !m.permission || auth.hasPermission(m.permission))
  })).filter(group => group.items.length > 0)
})

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
      <nav class="flex-1 overflow-y-auto custom-scrollbar py-4 px-2 space-y-4">
        <div v-for="group in visibleGroups" :key="group.name || 'main'" class="space-y-1">
          <!-- Group Label (Collapsible) -->
          <div 
            v-if="group.name && sidebarOpen" 
            class="px-3 py-2 flex items-center justify-between cursor-pointer group/label hover:bg-accent/30 rounded-lg transition-all"
            @click="toggleGroup(group.name)"
          >
            <span class="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/50 group-hover/label:text-primary transition-colors">
              {{ group.name }}
            </span>
            <ChevronDown 
              class="h-4 w-4 text-muted-foreground/60 transition-transform duration-500"
              :class="{ '-rotate-180': openGroups.includes(group.name) }"
            />
          </div>
          
          <!-- Items (Collapsible) -->
          <div 
            class="grid transition-all duration-200 ease-in-out"
            :class="[!group.name || !sidebarOpen || openGroups.includes(group.name) ? 'grid-rows-[1fr] opacity-100 mt-1' : 'grid-rows-[0fr] opacity-0']"
          >
            <div class="overflow-hidden space-y-1 px-1">
              <router-link
                v-for="item in group.items"
                :key="item.route"
                :to="item.route"
                :class="[
                  'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors relative group',
                  isActive(item.route)
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                ]"
              >
                <component :is="item.icon" class="h-5 w-5 shrink-0 transition-transform group-hover:scale-110" />
                <span v-if="sidebarOpen" class="truncate">{{ item.name }}</span>
                <div v-if="isActive(item.route)" class="absolute left-0 w-1 h-5 bg-primary rounded-r-full"></div>
              </router-link>
            </div>
          </div>
        </div>
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
          <nav class="py-4 px-2 space-y-4 overflow-y-auto h-full">
            <div v-for="group in visibleGroups" :key="group.name || 'main'" class="space-y-1">
              <div v-if="group.name" class="px-3 py-2 text-[10px] font-bold uppercase tracking-widest text-muted-foreground/60">
                {{ group.name }}
              </div>
              <router-link
                v-for="item in group.items" :key="item.route" :to="item.route"
                :class="[
                  'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium',
                  isActive(item.route) ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-accent'
                ]"
                @click="mobileSidebarOpen = false"
              >
                <component :is="item.icon" class="h-5 w-5 shrink-0" />
                {{ item.name }}
              </router-link>
            </div>
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
            <button @click="handleLogout" class="p-2 ml-1 text-destructive hover:bg-destructive/10 rounded-md" title="Keluar">
              <LogOut class="h-5 w-5" />
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
        <div class="flex-1 overflow-y-auto custom-scrollbar">
          <div class="p-4 lg:p-6 pb-20">
            <Breadcrumbs />
            <router-view />
          </div>
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

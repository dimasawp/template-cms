<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import Toaster from '@/components/ui/Toaster.vue'
import {
  LayoutDashboard, Users, Shield, Bell, Menu, X, LogOut, Sun, Moon
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const { isDark, toggleTheme } = useTheme()

const sidebarOpen = ref(true)
const mobileSidebarOpen = ref(false)

const menuItems = computed(() => [
  { name: 'Dashboard', icon: LayoutDashboard, route: '/dashboard', permission: null },
  { name: 'Users', icon: Users, route: '/users', permission: 'users.view' },
  { name: 'Roles', icon: Shield, route: '/roles', permission: 'roles.view' },
])

const visibleMenu = computed(() =>
  menuItems.value.filter(m => !m.permission || auth.hasPermission(m.permission))
)

function isActive(path: string) {
  return route.path === path
}

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
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
        <span v-if="sidebarOpen" class="text-lg font-bold text-primary">CMS Template</span>
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
            <span class="text-lg font-bold text-primary">CMS Template</span>
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

          <!-- Notification bell (placeholder) -->
          <button class="relative p-2 rounded-md hover:bg-accent">
            <Bell class="h-5 w-5" />
          </button>

          <!-- User menu -->
          <div class="flex items-center gap-2 ml-2">
            <div class="hidden sm:block text-right">
              <p class="text-sm font-medium">{{ auth.user?.full_name || auth.username }}</p>
              <p class="text-xs text-muted-foreground capitalize">{{ auth.userRole }}</p>
            </div>
            <button @click="handleLogout" class="p-2 rounded-md hover:bg-accent text-muted-foreground hover:text-foreground" title="Logout">
              <LogOut class="h-5 w-5" />
            </button>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex flex-1 flex-col overflow-hidden bg-muted/10">
        <div class="flex-1 overflow-y-auto p-4 lg:p-6">
          <router-view />
        </div>
        
        <!-- Footer -->
        <footer class="py-4 ps-4 text-start text-sm text-muted-foreground border-t bg-card/60">
          &copy; {{ new Date().getFullYear() }} CMS Template. Version 1.0.0
        </footer>
      </main>
    </div>
  </div>

  <Toaster />
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.slide-enter-active, .slide-leave-active { transition: transform 0.3s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(-100%); }
</style>

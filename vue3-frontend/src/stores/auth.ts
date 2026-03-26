import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export interface AuthUser {
  id: number
  username: string
  email: string | null
  full_name: string | null
  role_name: string
  permissions: string[]
  is_active: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value)
  const username = computed(() => user.value?.username || '')
  const userRole = computed(() => user.value?.role_name || '')
  const permissions = computed(() => user.value?.permissions || [])

  function hasPermission(perm: string): boolean {
    return permissions.value.includes(perm)
  }

  // Actions
  async function login(credentials: { username: string; password: string }) {
    isLoading.value = true
    error.value = null
    try {
      const { data: res } = await api.post('/auth/login', credentials)
      const tokens = res.data
      accessToken.value = tokens.access_token
      refreshToken.value = tokens.refresh_token
      localStorage.setItem('access_token', tokens.access_token)
      localStorage.setItem('refresh_token', tokens.refresh_token)
      await fetchCurrentUser()
      return true
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string; message?: string } } }
      error.value = e.response?.data?.message || e.response?.data?.detail || 'Login failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCurrentUser() {
    try {
      const { data: res } = await api.get('/auth/me')
      user.value = res.data
    } catch {
      clearAuth()
    }
  }

  async function logout() {
    try { await api.post('/auth/logout') } catch { /* ignore */ }
    clearAuth()
  }

  function clearAuth() {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function initialize() {
    if (accessToken.value) await fetchCurrentUser()
  }

  return {
    user, accessToken, refreshToken, isLoading, error,
    isAuthenticated, username, userRole, permissions,
    hasPermission, login, logout, fetchCurrentUser, clearAuth, initialize,
  }
})

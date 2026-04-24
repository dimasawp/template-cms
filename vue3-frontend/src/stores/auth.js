import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value)
  const username = computed(() => user.value?.username || '')
  const userRole = computed(() => user.value?.role_name || '')
  const permissions = computed(() => user.value?.permissions || [])

  function hasPermission(perm) {
    if (userRole.value === 'super_admin') return true
    return permissions.value.includes(perm)
  }

  // Actions
  async function login(credentials) {
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
    } catch (err) {
      error.value = err.response?.data?.message || err.response?.data?.detail || 'Login failed'
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

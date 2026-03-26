import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ── Auth (guest only) ──────────────────────────────────────────
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { requiresGuest: true },
    },
    {
      path: '/forgot-password',
      name: 'forgot-password',
      component: () => import('@/views/auth/ForgotPasswordView.vue'),
      meta: { requiresGuest: true },
    },

    // ── Dashboard (authenticated) ──────────────────────────────────
    {
      path: '/',
      component: () => import('@/layouts/DashboardLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '',          redirect: '/dashboard' },
        { path: 'dashboard', name: 'dashboard', component: () => import('@/views/dashboard/DashboardView.vue') },
        { path: 'components', name: 'components-doc', component: () => import('@/views/dashboard/ComponentsDocView.vue') },
        // Settings
        { path: 'users',    name: 'users',    component: () => import('@/views/settings/UsersView.vue'),    meta: { permission: 'users.view' } },
        { path: 'roles',    name: 'roles',    component: () => import('@/views/settings/RolesView.vue'),    meta: { permission: 'roles.view' } },
      ],
    },

    // ── Error pages ────────────────────────────────────────────────
    { path: '/403',         name: 'forbidden',  component: () => import('@/views/errors/ForbiddenView.vue') },
    { path: '/maintenance', name: 'maintenance', component: () => import('@/views/errors/MaintenanceView.vue') },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/errors/NotFoundView.vue') },
  ],
})

// ── Navigation Guards ──────────────────────────────────────────────

router.beforeEach(async (to, _from, next) => {
  const auth = useAuthStore()

  // Boot: load user if we have a token but haven't fetched yet
  if (auth.isAuthenticated && !auth.user) {
    await auth.initialize()
  }

  // Guest-only routes
  if (to.meta.requiresGuest && auth.isAuthenticated) {
    return next({ name: 'dashboard' })
  }

  // Auth-required routes
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next({ name: 'login' })
  }

  // Permission check
  if (to.meta.permission && auth.isAuthenticated) {
    if (!auth.hasPermission(to.meta.permission as string)) {
      return next({ name: 'forbidden' })
    }
  }

  next()
})

export default router

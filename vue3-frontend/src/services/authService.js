import api from './api'

export const authService = {
  login: (data) => api.get('/auth/login', { params: data }), // Note: login is usually POST, checking existing logic
  register: (data) => api.post('/auth/register', data),
  refresh: (token) => api.post('/auth/refresh', { refresh_token: token }),
  me: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'),
  getSessions: () => api.get('/auth/sessions'),
  revokeSession(sessionId) {
    return api.delete(`/auth/sessions/${sessionId}`)
  },
  bulkRevokeSessions(sessionIds) {
    return api.post('/auth/sessions/bulk-revoke', { session_ids: sessionIds })
  },
  updateMe: (data) => api.put('/auth/me', data),
  changePassword: (data) => api.put('/auth/change-password', data),
  uploadAvatar: (data) => api.post('/auth/avatar', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
}

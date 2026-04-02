import api from './api'

export interface LoginPayload { username: string; password: string }

export const authService = {
  login: (data: LoginPayload) => api.post('/auth/login', data),
  register: (data: any)      => api.post('/auth/register', data),
  refresh: (token: string)   => api.post('/auth/refresh', { refresh_token: token }),
  me: ()                     => api.get('/auth/me'),
  logout: ()                 => api.post('/auth/logout'),
  getSessions: ()            => api.get('/auth/sessions'),
  revokeSession(sessionId: number) {
    return api.delete(`/auth/sessions/${sessionId}`)
  },

  bulkRevokeSessions(sessionIds: number[]) {
    return api.post('/auth/sessions/bulk-revoke', { session_ids: sessionIds })
  },
  updateMe: (data: any)      => api.put('/auth/me', data),
  changePassword: (data: any)=> api.put('/auth/change-password', data),
  uploadAvatar:   (data: FormData) => api.post('/auth/avatar', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
}

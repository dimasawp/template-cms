import api from './api'

export interface LoginPayload { username: string; password: string }

export const authService = {
  login: (data: LoginPayload) => api.post('/auth/login', data),
  refresh: (token: string)   => api.post('/auth/refresh', { refresh_token: token }),
  me: ()                     => api.get('/auth/me'),
  logout: ()                 => api.post('/auth/logout'),
}

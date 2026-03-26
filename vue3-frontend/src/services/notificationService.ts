import api from './api'

export const notificationService = {
  getAll:     (params?: Record<string, unknown>) => api.get('/notifications', { params }),
  badge:      ()                                 => api.get('/notifications/badge'),
  markRead:   (id: number)                       => api.put(`/notifications/${id}/read`),
  markAllRead:()                                 => api.put('/notifications/read-all'),
}

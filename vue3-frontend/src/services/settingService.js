import api from './api'

export const settingService = {
  getPublic: () => api.get('/settings'),
  getRaw: () => api.get('/settings/raw'),
  update: (key, payload) => api.put(`/settings/${key}`, payload),
  bulkUpdate: (data) => api.post('/settings/bulk', { settings: data }),
}

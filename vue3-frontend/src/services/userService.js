import api from './api'

export const userService = {
  getAll: (params) => api.get('/users', { params }),
  getById: (id) => api.get(`/users/${id}`),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
  getRoles: () => api.get('/roles'),
  resetPassword: (id, data) => api.post(`/users/${id}/reset-password`, data),
  uploadAvatar: (id, file) => {
    const fd = new FormData()
    fd.append('file', file)
    return api.post(`/users/${id}/avatar`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  changePassword: (data) => api.put('/users/me/change-password', data),
}

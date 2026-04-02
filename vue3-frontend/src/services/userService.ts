import api from './api'

export const userService = {
  getAll:    (params?: Record<string, unknown>) => api.get('/users', { params }),
  getById:   (id: number)                       => api.get(`/users/${id}`),
  create:    (data: Record<string, unknown>)    => api.post('/users', data),
  update:    (id: number, data: Record<string, unknown>) => api.put(`/users/${id}`, data),
  delete:    (id: number)                       => api.delete(`/users/${id}`),
  getRoles:  ()                                 => api.get('/roles'),
  resetPassword: (id: number, data: { new_password: string }) => api.post(`/users/${id}/reset-password`, data),
  uploadAvatar:  (id: number, file: File) => {
    const fd = new FormData()
    fd.append('file', file)
    return api.post(`/users/${id}/avatar`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  changePassword: (data: { old_password: string; new_password: string }) => api.put('/users/me/change-password', data),
}

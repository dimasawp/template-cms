import api from './api'

export const roleService = {
  getAll:       (params?: Record<string, unknown>) => api.get('/roles', { params }),
  getById:      (id: number)                       => api.get(`/roles/${id}`),
  create:       (data: Record<string, unknown>)    => api.post('/roles', data),
  update:       (id: number, data: Record<string, unknown>) => api.put(`/roles/${id}`, data),
  delete:       (id: number)                       => api.delete(`/roles/${id}`),
  permissions:  ()                                 => api.get('/roles/permissions'),
}

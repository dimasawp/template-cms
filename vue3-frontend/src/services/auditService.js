import api from './api'

const auditService = {
  getLogs(params) {
    return api.get('/audit', { params })
  },

  getModules() {
    return api.get('/audit/modules')
  }
}

export default auditService

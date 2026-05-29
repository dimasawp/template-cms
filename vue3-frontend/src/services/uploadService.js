import api from './api'

export const uploadService = {
  uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    return api.post('/media/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

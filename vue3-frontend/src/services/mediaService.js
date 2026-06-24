import api from './api'

export const mediaService = {
  /**
   * Get paginated media list
   * @param {Object} params - Query params (skip, limit, search, file_type, sort_by, sort_order)
   */
  getAll(params) {
    return api.get('/media', { params })
  },

  /**
   * Upload a new media file
   * @param {File} file - The file to upload
   */
  upload(file) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/media/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * Delete a media file by ID
   * @param {Number} id - Media ID
   */
  delete(id) {
    return api.delete(`/media/${id}`)
  }
}

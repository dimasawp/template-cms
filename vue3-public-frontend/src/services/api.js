import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

export const publicService = {
  getPosts(params = {}) {
    return api.get('/public/posts', { params })
  },
  getPostDetail(slug) {
    return api.get(`/public/posts/${slug}`)
  },
  getCategories() {
    return api.get('/public/categories')
  },
  getSettings() {
    return api.get('/public/settings')
  }
}

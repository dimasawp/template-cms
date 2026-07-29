import api from './api'

export const captchaService = {
  generate: () => api.get('/captcha/generate'),
  verify: (token, answer) => api.post('/captcha/verify', { token, answer }),
}

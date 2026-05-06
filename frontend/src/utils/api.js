import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const analyzeText = (text) => api.post('/analyze', { text })
export const getHistory = (page = 1, limit = 20) => api.get(`/history?page=${page}&limit=${limit}`)
export const getDashboard = () => api.get('/dashboard')
export const login = (email, password) => api.post('/auth/login', { email, password })
export const register = (username, email, password) => api.post('/auth/register', { username, email, password })
export const getMe = () => api.get('/auth/me')
export const retrainModel = (model_type = 'logistic') => api.post('/train', { model_type })

export default api

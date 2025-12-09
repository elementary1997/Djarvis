import axios from 'axios'
import Cookies from 'js-cookie'

const API_URL = import.meta.env.VITE_API_URL || '/api'

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = Cookies.get('refresh_token')
        const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        })

        const { access } = response.data
        Cookies.set('access_token', access, { expires: 1 })

        originalRequest.headers.Authorization = `Bearer ${access}`
        return api(originalRequest)
      } catch (refreshError) {
        // Refresh failed, logout user
        Cookies.remove('access_token')
        Cookies.remove('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh_token: refreshToken }),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.patch('/auth/profile/', data),
  changePassword: (data) => api.post('/auth/change-password/', data),
  getStats: () => api.get('/auth/stats/'),
  getAchievements: () => api.get('/auth/achievements/'),
}

// Courses API
export const coursesAPI = {
  getModules: (params) => api.get('/courses/modules/', { params }),
  getModule: (slug) => api.get(`/courses/modules/${slug}/`),
  getLessons: (moduleSlug) => api.get(`/courses/modules/${moduleSlug}/lessons/`),
  getLesson: (moduleSlug, lessonSlug) => api.get(`/courses/modules/${moduleSlug}/lessons/${lessonSlug}/`),
}

// Exercises API
export const exercisesAPI = {
  getExercises: (params) => api.get('/exercises/', { params }),
  getExercise: (id) => api.get(`/exercises/${id}/`),
  getAttempts: (exerciseId) => api.get(`/exercises/${exerciseId}/attempts/`),
  getHint: (exerciseId, hintIndex) => api.post(`/exercises/${exerciseId}/hint/`, { hint_index: hintIndex }),
}

// Sandbox API
export const sandboxAPI = {
  createSandbox: () => api.post('/sandbox/create/'),
  executeCode: (data) => api.post('/sandbox/execute/', data),
  destroySandbox: () => api.post('/sandbox/destroy/'),
}

// Progress API
export const progressAPI = {
  getOverview: () => api.get('/progress/overview/'),
  getModuleProgress: () => api.get('/progress/modules/'),
  getLessonProgress: (params) => api.get('/progress/lessons/', { params }),
  markLessonComplete: (data) => api.post('/progress/lessons/complete/', data),
  getStreak: () => api.get('/progress/streak/'),
  getLeaderboard: () => api.get('/progress/leaderboard/'),
}

export default api

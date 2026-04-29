import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    console.error('API Error:', err)
    return Promise.reject(err)
  }
)

export const getDashboard = () => api.get('/dashboard')
export const getPlatforms = () => api.get('/platforms')
export const getPlatform = (id) => api.get(`/platforms/${id}`)
export const createPlatform = (data) => api.post('/platforms', data)
export const updatePlatform = (id, data) => api.put(`/platforms/${id}`, data)
export const deletePlatform = (id) => api.delete(`/platforms/${id}`)

export const getNovels = (params) => api.get('/novels', { params })
export const getNovel = (id) => api.get(`/novels/${id}`)
export const getRanking = (params) => api.get('/novels/ranking', { params })

export const getTasks = (params) => api.get('/tasks', { params })
export const runScrape = (platformId, rankType = 'hot') =>
  api.post('/tasks/run', null, { params: { platform_id: platformId, rank_type: rankType } })
export const runScrapeAll = (rankType = 'hot') =>
  api.post('/tasks/run-all', null, { params: { rank_type: rankType } })

export default api

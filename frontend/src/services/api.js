/**
 * API Service
 * Handles all backend API calls
 */
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Budget API
export const budgetAPI = {
  uploadCSV: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/api/budget/upload-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  analyze: async (transactions, monthlyIncome = null) => {
    const response = await api.post('/api/budget/analyze', {
      transactions,
      monthly_income: monthlyIncome,
    })
    return response.data
  },

  categorize: async (transaction) => {
    const response = await api.post('/api/budget/categorize', transaction)
    return response.data
  },
}

// Goals API
export const goalsAPI = {
  create: async (goalData) => {
    const response = await api.post('/api/goals/create', goalData)
    return response.data
  },

  update: async (goalId, amount, note = null) => {
    const response = await api.post(`/api/goals/${goalId}/update`, {
      amount,
      note,
    })
    return response.data
  },

  get: async (goalId) => {
    const response = await api.get(`/api/goals/${goalId}`)
    return response.data
  },

  prioritize: async (goals) => {
    const response = await api.post('/api/goals/prioritize', goals)
    return response.data
  },
}

// Health Score API
export const healthAPI = {
  calculate: async (data) => {
    const response = await api.post('/api/health-score/calculate', data)
    return response.data
  },

  getBenchmarks: async () => {
    const response = await api.get('/api/health-score/benchmark')
    return response.data
  },
}

// Chat API
export const chatAPI = {
  sendMessage: async (message, conversationHistory = []) => {
    const response = await api.post('/api/chat/', {
      message,
      conversation_history: conversationHistory,
    })
    return response.data
  },

  searchKnowledge: async (query) => {
    const response = await api.get('/api/chat/knowledge-search', {
      params: { query },
    })
    return response.data
  },
}

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health')
  return response.data
}

export default api

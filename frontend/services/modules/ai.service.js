import { API_CONFIG, API_ENDPOINTS } from '@/config/api.config.js'
import { request } from '@/services/request.js'

export function sendAiMessage(data) {
  return request({ url: API_ENDPOINTS.ai.chat, method: 'POST', data, timeout: API_CONFIG.aiTimeout })
}

export function getAiAdvice() {
  return request({ url: API_ENDPOINTS.ai.advice })
}

import { API_ENDPOINTS } from '@/config/api.config.js'
import { request } from '@/services/request.js'

export function getHealthProfile() {
  return request({ url: API_ENDPOINTS.health.profile })
}

export function saveHealthProfile(data) {
  return request({ url: API_ENDPOINTS.health.profile, method: 'POST', data })
}

export function getHealthRecords() {
  return request({ url: API_ENDPOINTS.health.records })
}

export function getHealthMetrics() {
  return request({ url: API_ENDPOINTS.health.metrics })
}

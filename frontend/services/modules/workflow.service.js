import { API_ENDPOINTS } from '@/config/api.config.js'
import { request } from '@/services/request.js'

export function verifyFields(fields) {
  return request({ url: API_ENDPOINTS.workflow.verify, method: 'POST', data: { fields } })
}

export function inspectCabinet(medicines) {
  return request({ url: API_ENDPOINTS.workflow.cabinet, method: 'POST', data: { medicines } })
}

export function analyzeTrends(records) {
  return request({ url: API_ENDPOINTS.workflow.trends, method: 'POST', data: { records } })
}

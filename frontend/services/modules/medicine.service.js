import { API_ENDPOINTS } from '@/config/api.config.js'
import { request } from '@/services/request.js'

export function getMedicines() {
  return request({ url: API_ENDPOINTS.medicine.list })
}

export function createMedicine(data) {
  return request({ url: API_ENDPOINTS.medicine.create, method: 'POST', data })
}

export function updateMedicine(id, data) {
  return request({ url: API_ENDPOINTS.medicine.update.replace(':id', id), method: 'PUT', data })
}

export function removeMedicine(id) {
  return request({ url: API_ENDPOINTS.medicine.remove.replace(':id', id), method: 'DELETE' })
}

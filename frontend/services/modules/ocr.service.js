import { API_ENDPOINTS } from '@/config/api.config.js'
import { request, uploadFile } from '@/services/request.js'

export function scanReport(filePath, formData = {}) {
  return uploadFile({
    url: API_ENDPOINTS.ocr.scanReport,
    filePath,
    formData
  })
}

export function scanMedicine(filePath, formData = {}) {
  return uploadFile({
    url: API_ENDPOINTS.ocr.scanMedicine,
    filePath,
    formData
  })
}

export function confirmOcrResult(data) {
  return request({
    url: API_ENDPOINTS.ocr.confirm,
    method: 'POST',
    data
  })
}

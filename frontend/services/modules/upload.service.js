import { API_ENDPOINTS } from '@/config/api.config.js'
import { uploadFile } from '@/services/request.js'

export function uploadPhoto(filePath) {
  return uploadFile({
    url: API_ENDPOINTS.upload.photo,
    filePath,
    useAuth: false,
    loadingText: '上传图片中'
  })
}

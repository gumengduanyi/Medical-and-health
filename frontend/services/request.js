import { API_CONFIG } from '@/config/api.config.js'
import { clearAuthSession, getAuthToken } from '@/store/user.js'

function buildUrl(url) {
  if (/^https?:\/\//.test(url)) return url
  return `${API_CONFIG.baseURL}${url}`
}

function normalizeError(error = {}) {
  const data = error.data || {}
  return {
    statusCode: error.statusCode || 0,
    code: data.code || error.errCode || 'REQUEST_ERROR',
    message: data.message || data.detail || error.errMsg || error.message || '请求失败',
    data
  }
}

function buildHeader(header = {}, useAuth = true, contentType = 'application/json') {
  const token = useAuth ? getAuthToken() : ''
  return {
    ...(contentType ? { 'Content-Type': contentType } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...header
  }
}

function handleAuthExpired(error) {
  if (error.statusCode === 401) {
    clearAuthSession()
  }
}

function runWithLoading(title, task) {
  if (!title) return task()
  uni.showLoading({ title, mask: true })
  return task().finally(() => uni.hideLoading())
}

export function request(options = {}) {
  const {
    url,
    method = 'GET',
    data = {},
    header = {},
    timeout = API_CONFIG.timeout,
    loadingText = '',
    useAuth = true
  } = options

  return runWithLoading(loadingText, () => new Promise((resolve, reject) => {
    uni.request({
      url: buildUrl(url),
      method,
      data,
      timeout,
      header: buildHeader(header, useAuth),
      success(response) {
        const { statusCode, data: responseData } = response
        if (statusCode >= 200 && statusCode < 300) {
          resolve(responseData)
          return
        }
        const error = normalizeError({ statusCode, data: responseData })
        handleAuthExpired(error)
        reject(error)
      },
      fail(error) {
        reject(normalizeError(error))
      }
    })
  }))
}

export function uploadFile(options = {}) {
  const {
    url,
    filePath,
    name = 'file',
    formData = {},
    header = {},
    loadingText = '',
    useAuth = true
  } = options

  return runWithLoading(loadingText, () => new Promise((resolve, reject) => {
    uni.uploadFile({
      url: buildUrl(url),
      filePath,
      name,
      formData,
      timeout: API_CONFIG.uploadTimeout,
      header: buildHeader(header, useAuth, ''),
      success(response) {
        const { statusCode } = response
        let responseData = response.data
        try {
          responseData = JSON.parse(response.data)
        } catch (e) {}

        if (statusCode >= 200 && statusCode < 300) {
          resolve(responseData)
          return
        }

        const error = normalizeError({ statusCode, data: responseData })
        handleAuthExpired(error)
        reject(error)
      },
      fail(error) {
        reject(normalizeError(error))
      }
    })
  }))
}

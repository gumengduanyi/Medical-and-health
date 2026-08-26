export const ENV = {
  DEV: 'development',
  PROD: 'production'
}

export const API_CONFIG = {
  baseURL: 'http://localhost:8000/api',
  timeout: 15000,
  uploadTimeout: 600000
}

export const API_ENDPOINTS = {
  ocr: {
    scanReport: '/ocr/reports/scan',
    scanMedicine: '/ocr/medicines/scan',
    confirm: '/ocr/confirm'
  },
  upload: {
    qrcode: '/upload/qrcode',
    photo: '/upload/photo'
  },
  health: {
    profile: '/health/profile',
    records: '/health/records',
    metrics: '/health/metrics'
  },
  medicine: {
    list: '/medicines',
    create: '/medicines',
    update: '/medicines/:id',
    remove: '/medicines/:id'
  },
  ai: {
    chat: '/ai/chat',
    advice: '/ai/advice'
  },
  auth: {
    wechatLogin: '/auth/wechat-login',
    me: '/auth/me',
    logout: '/auth/logout'
  }
}

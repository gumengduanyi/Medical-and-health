export const ENV = {
  DEV: 'development',
  PROD: 'production'
}

export const API_CONFIG = {
  baseURL: 'http://172.20.10.2:8000/api',
  timeout: 15000,
  aiTimeout: 180000,
  uploadTimeout: 600000
}

export const API_ENDPOINTS = {
  ocr: {
    scanReport: '/ocr/reports/scan',
    scanMedicine: '/ocr/medicines/scan',
    job: '/ocr/jobs/:id',
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
  workflow: {
    verify: '/workflows/verify',
    cabinet: '/workflows/cabinet',
    trends: '/workflows/trends'
  },
  leaflet: {
    discover: '/leaflets/auto-discover',
    importBaike: '/leaflets/import-baike',
    list: '/leaflets',
    approve: '/leaflets/:id/approve'
  },
  auth: {
    wechatLogin: '/auth/wechat-login',
    me: '/auth/me',
    logout: '/auth/logout'
  }
}

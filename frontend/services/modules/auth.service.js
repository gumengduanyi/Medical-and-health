import { API_ENDPOINTS } from '@/config/api.config.js'
import { request } from '@/services/request.js'
import { clearAuthSession, setAuthSession, setCurrentUser } from '@/store/user.js'

export function loginWithWechat(extraData = {}) {
  return new Promise((resolve, reject) => {
    uni.login({
      provider: 'weixin',
      success: async ({ code }) => {
        try {
          const response = await request({
            url: API_ENDPOINTS.auth.wechatLogin,
            method: 'POST',
            data: { code, ...extraData },
            useAuth: false,
            loadingText: '登录中'
          })
          setAuthSession({ token: response.token || response.access_token || '', user: response.user || null })
          resolve(response)
        } catch (error) {
          reject(error)
        }
      },
      fail(error) {
        reject({ message: error.errMsg || '微信登录失败', data: error })
      }
    })
  })
}

export async function fetchCurrentUser() {
  const user = await request({ url: API_ENDPOINTS.auth.me })
  setCurrentUser(user)
  return user
}

export async function logout() {
  try {
    await request({ url: API_ENDPOINTS.auth.logout, method: 'POST' })
  } finally {
    clearAuthSession()
  }
}

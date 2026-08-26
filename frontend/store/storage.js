const STORAGE_KEYS = {
  healthProfile: 'health_profile',
  medicines: 'medicines',
  floatingActionPosition: 'floating_action_position',
  authToken: 'auth_token',
  currentUser: 'current_user'
}

export function getStorage(key, defaultValue = null) {
  try {
    const value = uni.getStorageSync(key)
    return value || defaultValue
  } catch (e) {
    return defaultValue
  }
}

export function setStorage(key, value) {
  try {
    uni.setStorageSync(key, value)
    return true
  } catch (e) {
    return false
  }
}

export function removeStorage(key) {
  try {
    uni.removeStorageSync(key)
    return true
  } catch (e) {
    return false
  }
}

export { STORAGE_KEYS }

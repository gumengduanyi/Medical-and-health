import { getStorage, removeStorage, setStorage, STORAGE_KEYS } from '@/store/storage.js'

const state = {
  token: getStorage(STORAGE_KEYS.authToken, ''),
  user: getStorage(STORAGE_KEYS.currentUser, null)
}

const listeners = []

function notify() {
  listeners.forEach((listener) => listener(getUserState()))
}

export function getUserState() {
  return {
    token: state.token,
    user: state.user,
    isLoggedIn: Boolean(state.token)
  }
}

export function getAuthToken() {
  return state.token || ''
}

export function setAuthSession({ token = '', user = null } = {}) {
  state.token = token
  state.user = user
  setStorage(STORAGE_KEYS.authToken, token)
  setStorage(STORAGE_KEYS.currentUser, user)
  notify()
}

export function setCurrentUser(user) {
  state.user = user
  setStorage(STORAGE_KEYS.currentUser, user)
  notify()
}

export function clearAuthSession() {
  state.token = ''
  state.user = null
  removeStorage(STORAGE_KEYS.authToken)
  removeStorage(STORAGE_KEYS.currentUser)
  notify()
}

export function subscribeUser(listener) {
  if (typeof listener !== 'function') return () => {}
  listeners.push(listener)
  listener(getUserState())
  return () => {
    const index = listeners.indexOf(listener)
    if (index >= 0) listeners.splice(index, 1)
  }
}

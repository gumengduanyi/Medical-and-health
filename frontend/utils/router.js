import { TAB_ROUTES as TAB_ROUTE_LIST } from '@/constants/routes.js'

const TAB_ROUTES = new Set(TAB_ROUTE_LIST)

let navigating = false

function normalizeUrl(url = '') {
  return url.split('?')[0]
}

function canNavigate() {
  if (navigating) return false
  navigating = true
  return true
}

function releaseNavigateLock() {
  navigating = false
}

export function smoothSwitchTab(url) {
  const target = normalizeUrl(url)
  const pages = getCurrentPages()
  const current = pages.length ? `/${pages[pages.length - 1].route}` : ''

  if (current === target) return
  if (!canNavigate()) return

  uni.switchTab({
    url: target,
    complete() {
      releaseNavigateLock()
    }
  })
}

export function smoothNavigateTo(url) {
  const target = normalizeUrl(url)
  if (TAB_ROUTES.has(target)) {
    smoothSwitchTab(url)
    return
  }
  if (!canNavigate()) return

  uni.navigateTo({
    url,
    complete: releaseNavigateLock
  })
}

import { API_ENDPOINTS } from '@/config/api.config.js'
import { request } from '@/services/request.js'

export function importBaikeLeaflet(data) {
  return request({
    url: API_ENDPOINTS.leaflet.importBaike,
    method: 'POST',
    data,
    loadingText: '导入说明书中'
  })
}

export function discoverLeaflet(data) {
  return request({
    url: API_ENDPOINTS.leaflet.discover,
    method: 'POST',
    data,
    loadingText: '查找说明书中'
  })
}

export function approveLeaflet(id, note = '') {
  return request({
    url: API_ENDPOINTS.leaflet.approve.replace(':id', id),
    method: 'POST',
    data: { note },
    loadingText: '审核说明书中'
  })
}
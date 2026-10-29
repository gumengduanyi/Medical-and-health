<template>
  <view class="page-container">
    <view class="custom-nav">
      <view class="status-bar"></view>
      <view class="nav-content">
        <view class="nav-back" @click="goBack"><text class="nav-back-icon">‹</text></view>
        <text class="nav-title">{{ category || '档案详情' }}</text>
        <view class="nav-placeholder"></view>
      </view>
    </view>

    <view class="page-content">
      <view v-if="reports.length" class="report-list">
        <view class="report-card" v-for="item in reports" :key="item.id">
          <image
            v-if="thumb(item)"
            class="report-thumb"
            :src="thumb(item)"
            mode="aspectFill"
            @click="previewImages(item, 0)"
          />
          <view class="report-body">
            <text class="report-title">{{ item.name }}</text>
            <view class="report-tags">
              <text class="report-tag">{{ item.category }}</text>
              <text class="report-meta">{{ formatDate(item.reportTime) }}</text>
            </view>
            <text class="report-desc">录入于 {{ formatDate(item.entryTime) }}</text>
            <text class="report-count">{{ item.images.length }} 张图片 · {{ item.files.length }} 个文件</text>
          </view>
        </view>
      </view>
      <view v-else-if="!loading" class="empty-state">
        <text class="empty-emoji">🐱</text>
        <text class="empty-text">该分类下还没有报告，去档案智能录入添加吧</text>
      </view>
    </view>
  </view>
</template>

<script>
import { API_CONFIG } from '@/config/api.config.js'
import { getReports } from '@/services/modules/health.service.js'

export default {
  data() {
    return {
      category: '',
      reports: [],
      loading: false
    }
  },
  onLoad(options = {}) {
    this.category = options.category ? decodeURIComponent(options.category) : ''
    this.loadReports()
  },
  methods: {
    goBack() { uni.navigateBack() },
    async loadReports() {
      this.loading = true
      try {
        const result = await getReports(this.category)
        this.reports = (Array.isArray(result) ? result : []).map((item) => ({
          ...item,
          images: Array.isArray(item.images) ? item.images : [],
          files: Array.isArray(item.files) ? item.files : []
        }))
      } catch (error) {
        uni.showToast({ title: error?.message || '报告加载失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    thumb(item) {
      const first = item.images && item.images[0]
      return first && first.url ? this.toFullUrl(first.url) : ''
    },
    previewImages(item, index) {
      const urls = item.images.map((image) => this.toFullUrl(image.url)).filter(Boolean)
      if (!urls.length) return
      uni.previewImage({ urls, current: urls[index] })
    },
    toFullUrl(url) {
      if (!url) return ''
      if (/^https?:\/\//.test(url)) return url
      return `${API_CONFIG.baseURL.replace(/\/api$/, '')}${url}`
    },
    formatDate(value) {
      if (!value) return '未标注时间'
      return String(value).slice(0, 16)
    }
  }
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: #F4F7F5; }
.custom-nav { position: fixed; top: 0; left: 0; right: 0; z-index: 999; background: rgba(244, 247, 245, 0.92); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-bottom: 1rpx solid #DDE7E1; }
.status-bar { height: var(--status-bar-height); }
.nav-content { height: 100rpx; padding: 0 32rpx; display: flex; align-items: center; justify-content: space-between; }
.nav-back { width: 60rpx; height: 60rpx; display: flex; align-items: center; justify-content: center; }
.nav-back-icon { font-size: 56rpx; color: #17231F; font-weight: 300; line-height: 1; }
.nav-placeholder { width: 60rpx; }
.nav-title { position: absolute; left: 50%; transform: translateX(-50%); font-size: 36rpx; font-weight: 700; color: #17231F; }
.page-content { padding: 32rpx; padding-top: calc(var(--status-bar-height) + 100rpx + 32rpx); padding-bottom: 80rpx; }

.report-list { display: flex; flex-direction: column; gap: 20rpx; }
.report-card { display: flex; gap: 22rpx; padding: 24rpx; border-radius: 20rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 8rpx 20rpx rgba(31, 72, 55, 0.04); }
.report-thumb { width: 132rpx; height: 132rpx; border-radius: 14rpx; background: #F4F7F5; flex-shrink: 0; }
.report-body { flex: 1; min-width: 0; }
.report-title { display: block; color: #17231F; font-size: 30rpx; font-weight: 700; word-break: break-all; }
.report-tags { display: flex; align-items: center; gap: 14rpx; margin-top: 12rpx; }
.report-tag { padding: 6rpx 14rpx; border-radius: 999rpx; background: #E1F3ED; color: #0E7F72; font-size: 21rpx; }
.report-meta { color: #71817A; font-size: 23rpx; }
.report-desc { display: block; margin-top: 10rpx; color: #9AA8A1; font-size: 23rpx; }
.report-count { display: block; margin-top: 8rpx; color: #50605A; font-size: 23rpx; }

.empty-state { display: flex; flex-direction: column; align-items: center; padding: 140rpx 40rpx; }
.empty-emoji { font-size: 76rpx; line-height: 1; }
.empty-text { margin-top: 24rpx; color: #9AA8A1; font-size: 25rpx; text-align: center; line-height: 1.6; }
</style>

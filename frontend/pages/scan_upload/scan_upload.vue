<template>
  <view class="page-container">
    <view class="custom-nav">
      <view class="status-bar"></view>
      <view class="nav-content">
        <view class="nav-back" @click="goBack"><text class="nav-back-icon">‹</text></view>
        <text class="nav-title">扫码拍照上传</text>
        <view class="nav-placeholder"></view>
      </view>
    </view>

    <view class="page-content">
      <text class="page-desc">手机扫码后可拍摄或选择健康报告、药盒等图片上传。</text>

      <view class="qr-section">
        <image class="qr-image" :src="qrCodeUrl" mode="aspectFit" @error="onQrError" />
        <text class="qr-hint">使用手机微信扫描二维码</text>
        <text class="scan-url">{{ scanUrl }}</text>
        <view class="action-row">
          <view class="action-button" @click="refreshQrCode">刷新</view>
          <view class="action-button secondary" @click="copyUrl">复制地址</view>
        </view>
      </view>

      <view class="steps-section">
        <text class="section-title">上传流程</text>
        <view v-for="(step, index) in steps" :key="step" class="step-row">
          <text class="step-number">{{ index + 1 }}</text>
          <text class="step-text">{{ step }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { API_CONFIG } from '@/config/api.config.js'

export default {
  data() {
    return {
      timestamp: Date.now(),
      steps: ['手机扫描二维码', '拍照或从相册选择图片', '上传后可在电脑端继续识别']
    }
  },
  computed: {
    qrCodeUrl() {
      return `${API_CONFIG.baseURL}/upload/qrcode?t=${this.timestamp}`
    },
    scanUrl() {
      return `${API_CONFIG.baseURL.replace(/\/api$/, '')}/upload/camera`
    }
  },
  methods: {
    goBack() { uni.navigateBack() },
    refreshQrCode() {
      this.timestamp = Date.now()
    },
    copyUrl() {
      uni.setClipboardData({ data: this.scanUrl })
    },
    onQrError() {
      uni.showToast({ title: '二维码加载失败', icon: 'none' })
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
.page-desc { display: block; font-size: 26rpx; color: #71817A; line-height: 1.6; }

.qr-section { margin-top: 32rpx; display: flex; flex-direction: column; align-items: center; padding: 48rpx 32rpx; border-radius: 22rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 10rpx 24rpx rgba(31, 72, 55, 0.05); }
.qr-image { width: 440rpx; height: 440rpx; border-radius: 16rpx; background: #fff; }
.qr-hint { margin-top: 28rpx; color: #17231F; font-size: 30rpx; font-weight: 700; }
.scan-url { width: 100%; margin-top: 12rpx; color: #9AA8A1; font-size: 22rpx; text-align: center; word-break: break-all; }
.action-row { display: flex; gap: 16rpx; margin-top: 32rpx; }
.action-button { min-width: 160rpx; height: 72rpx; display: flex; align-items: center; justify-content: center; border-radius: 14rpx; background: #0E9F8E; color: #FFFFFF; font-size: 26rpx; font-weight: 700; }
.action-button.secondary { background: #F4F7F5; color: #50605A; border: 1rpx solid #DDE7E1; }

.steps-section { margin-top: 32rpx; padding: 32rpx; border-radius: 22rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 10rpx 24rpx rgba(31, 72, 55, 0.05); }
.section-title { display: block; color: #17231F; font-size: 30rpx; font-weight: 700; }
.step-row { display: flex; align-items: center; gap: 20rpx; margin-top: 24rpx; }
.step-number { display: inline-flex; width: 44rpx; height: 44rpx; border-radius: 50%; align-items: center; justify-content: center; background: #E1F3ED; color: #0E9F8E; font-size: 24rpx; font-weight: 700; flex-shrink: 0; }
.step-text { color: #50605A; font-size: 27rpx; }
</style>

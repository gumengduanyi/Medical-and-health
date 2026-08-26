<template>
  <view class="page-container">
    <view class="page-header">
      <text class="page-title">扫码拍照上传</text>
      <text class="page-desc">手机扫码后可拍摄或选择健康报告、药盒等图片上传。</text>
    </view>

    <view class="qr-section">
      <image class="qr-image" :src="qrCodeUrl" mode="aspectFit" @error="onQrError" />
      <text class="qr-hint">使用手机微信扫描二维码</text>
      <text class="scan-url">{{ scanUrl }}</text>
      <view class="action-row">
        <button class="action-button" @click="refreshQrCode">刷新</button>
        <button class="action-button secondary" @click="copyUrl">复制地址</button>
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
.page-container { min-height: 100vh; padding: 32rpx 28rpx 80rpx; background: #f8fafc; box-sizing: border-box; }
.page-header { padding-bottom: 32rpx; border-bottom: 2rpx solid #e2e8f0; }
.page-title { display: block; color: #1e293b; font-size: 40rpx; font-weight: 700; }
.page-desc { display: block; margin-top: 12rpx; color: #64748b; font-size: 26rpx; line-height: 1.6; }
.qr-section { display: flex; flex-direction: column; align-items: center; padding: 40rpx 0; border-bottom: 2rpx solid #e2e8f0; }
.qr-image { width: 440rpx; height: 440rpx; }
.qr-hint { margin-top: 24rpx; color: #1e293b; font-size: 30rpx; font-weight: 700; }
.scan-url { width: 100%; margin-top: 12rpx; color: #64748b; font-size: 22rpx; text-align: center; word-break: break-all; }
.action-row { display: flex; gap: 16rpx; margin-top: 28rpx; }
.action-button { min-width: 160rpx; height: 72rpx; margin: 0; border-radius: 6rpx; background: #0f766e; color: #fff; font-size: 26rpx; line-height: 72rpx; }
.action-button.secondary { background: #e2e8f0; color: #334155; }
.steps-section { padding: 32rpx 0; }
.section-title { display: block; color: #1e293b; font-size: 30rpx; font-weight: 700; }
.step-row { display: flex; align-items: center; gap: 18rpx; margin-top: 24rpx; }
.step-number { display: inline-flex; width: 42rpx; height: 42rpx; border-radius: 50%; align-items: center; justify-content: center; background: #d1fae5; color: #047857; font-size: 24rpx; font-weight: 700; }
.step-text { color: #475569; font-size: 27rpx; }
</style>

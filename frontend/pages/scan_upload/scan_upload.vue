<template>
  <view class="page-container">
    <view class="custom-nav">
      <view class="status-bar"></view>
      <view class="nav-content">
        <view class="nav-back" @click="goBack"><text class="nav-back-icon">‹</text></view>
        <text class="nav-title">拍照上传</text>
        <view class="nav-placeholder"></view>
      </view>
    </view>

    <view class="page-content">
      <text class="page-desc">拍摄或选择健康报告、药盒等图片后上传，上传后可在电脑端继续识别。</text>

      <view class="upload-section">
        <view class="upload-button" @click="openPicker">
          <text class="upload-button-icon">＋</text>
          <text class="upload-button-text">选择图片上传</text>
        </view>
        <text class="upload-hint">可选择拍照或从相册选择，首次使用需确认相机与相册权限</text>
        <image v-if="previewUrl" class="preview" :src="previewUrl" mode="aspectFit" />
        <text v-if="statusText" class="status" :class="statusType">{{ statusText }}</text>
        <text v-if="uploadedUrl" class="upload-link" @click="previewUploaded">查看已上传图片</text>
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
import { uploadPhoto } from '@/services/modules/upload.service.js'

const SCOPE_TIPS = {
  'scope.camera': '拍照需要使用摄像头'
}

export default {
  data() {
    return {
      previewUrl: '',
      statusText: '',
      statusType: '',
      uploadedUrl: '',
      uploading: false,
      steps: ['点击按钮选择拍照或从相册选择', '首次使用需确认相机与相册权限', '上传成功后可在电脑端继续识别']
    }
  },
  methods: {
    goBack() { uni.navigateBack() },
    openPicker() {
      if (this.uploading) return
      uni.showActionSheet({
        itemList: ['拍照', '从相册选择'],
        success: ({ tapIndex }) => {
          if (tapIndex === 0) this.takePhoto()
          else this.pickFromAlbum()
        }
      })
    },
    async takePhoto() {
      if (!await this.ensureAuthorization('scope.camera')) return
      this.chooseImage(['camera'])
    },
    pickFromAlbum() {
      this.chooseImage(['album'])
    },
    ensureAuthorization(scope) {
      return new Promise((resolve) => {
        if (typeof uni.getSetting !== 'function' || typeof uni.authorize !== 'function') return resolve(true)
        uni.getSetting({
          success: (setting) => {
            const state = (setting.authSetting || {})[scope]
            if (state === true) return resolve(true)
            if (state === false) return this.guideToSetting(scope).then(resolve)
            uni.authorize({
              scope,
              success: () => resolve(true),
              fail: (error) => {
                if (/deny/i.test((error && error.errMsg) || '')) return this.guideToSetting(scope).then(resolve)
                // App、H5 等不支持 uni.authorize 的平台：交给系统在真正调用时申请
                resolve(true)
              }
            })
          },
          fail: () => resolve(true)
        })
      })
    },
    guideToSetting(scope) {
      const tip = SCOPE_TIPS[scope] || '需要相关权限'
      return new Promise((resolve) => {
        uni.showModal({
          title: '权限申请',
          content: `${tip}，请在设置中开启后重试`,
          confirmText: '去设置',
          success: (res) => {
            if (!res.confirm || typeof uni.openSetting !== 'function') return resolve(false)
            uni.openSetting({
              success: (setting) => resolve((setting.authSetting || {})[scope] === true),
              fail: () => resolve(false)
            })
          },
          fail: () => resolve(false)
        })
      })
    },
    chooseImage(sourceType) {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed', 'original'],
        sourceType,
        success: (res) => {
          const filePath = (res.tempFilePaths || [])[0]
          if (filePath) this.uploadImage(filePath)
        },
        fail: (error) => {
          if (/deny|permission/i.test((error && error.errMsg) || '')) {
            uni.showToast({ title: '请在系统设置中开启权限', icon: 'none' })
          }
        }
      })
    },
    async uploadImage(filePath) {
      this.uploading = true
      this.previewUrl = filePath
      this.uploadedUrl = ''
      this.statusType = ''
      this.statusText = ''
      try {
        const result = await uploadPhoto(filePath)
        this.statusType = 'success'
        this.statusText = '上传成功'
        this.uploadedUrl = this.toFullUrl(result && result.url)
      } catch (error) {
        this.statusType = 'error'
        this.statusText = (error && error.message) || '上传失败'
      } finally {
        this.uploading = false
      }
    },
    toFullUrl(url) {
      if (!url) return ''
      if (/^https?:\/\//.test(url)) return url
      return `${API_CONFIG.baseURL.replace(/\/api$/, '')}${url}`
    },
    previewUploaded() {
      if (!this.uploadedUrl) return
      uni.previewImage({ urls: [this.uploadedUrl] })
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

.upload-section { margin-top: 32rpx; display: flex; flex-direction: column; align-items: center; padding: 48rpx 32rpx; border-radius: 22rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 10rpx 24rpx rgba(31, 72, 55, 0.05); }
.upload-button { width: 100%; height: 96rpx; display: flex; align-items: center; justify-content: center; gap: 12rpx; border-radius: 16rpx; background: #0E9F8E; }
.upload-button-icon { color: #FFFFFF; font-size: 40rpx; line-height: 1; }
.upload-button-text { color: #FFFFFF; font-size: 30rpx; font-weight: 700; }
.upload-hint { margin-top: 20rpx; color: #9AA8A1; font-size: 22rpx; text-align: center; line-height: 1.6; }
.preview { width: 100%; margin-top: 28rpx; border-radius: 16rpx; background: #F4F7F5; }
.status { margin-top: 20rpx; font-size: 26rpx; font-weight: 600; }
.status.success { color: #047857; }
.status.error { color: #B91C1C; }
.upload-link { margin-top: 16rpx; color: #2563EB; font-size: 26rpx; }

.steps-section { margin-top: 32rpx; padding: 32rpx; border-radius: 22rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 10rpx 24rpx rgba(31, 72, 55, 0.05); }
.section-title { display: block; color: #17231F; font-size: 30rpx; font-weight: 700; }
.step-row { display: flex; align-items: center; gap: 20rpx; margin-top: 24rpx; }
.step-number { display: inline-flex; width: 44rpx; height: 44rpx; border-radius: 50%; align-items: center; justify-content: center; background: #E1F3ED; color: #0E9F8E; font-size: 24rpx; font-weight: 700; flex-shrink: 0; }
.step-text { color: #50605A; font-size: 27rpx; }
</style>

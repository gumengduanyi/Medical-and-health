<template>
  <view class="page-container">
    <view class="custom-nav">
      <view class="status-bar"></view>
      <view class="nav-content">
        <view class="nav-back" @click="goBack"><text class="nav-back-icon">‹</text></view>
        <text class="nav-title">药品录入</text>
        <view class="nav-placeholder"></view>
      </view>
    </view>

    <view class="page-content">
    <view class="form-card">
      <text class="card-title">基础信息</text>
      <view class="form-item"><text class="label">药品名称</text><input v-model="medicine.name" placeholder="如：阿司匹林肠溶片" /></view>
      <view class="form-item"><text class="label">用法用量</text><input v-model="medicine.dose" placeholder="如：0.1g × 1片，饭后" /></view>
      <view class="form-item"><text class="label">库存比例</text><input v-model="medicine.stock" type="number" placeholder="如：60" /></view>
      <view class="form-item"><text class="label">有效期</text><input v-model="medicine.expire" placeholder="如：2027-12-10" /></view>
    </view>

    <view class="ai-card">
      <text class="ai-title">AI 风险校验</text>
      <text class="ai-desc">保存后将结合个人过敏史、既往病史和诊断记录，检查禁忌、重复用药和相互作用。</text>
      <view class="risk-tags">
        <text class="risk-tag">低库存提醒</text>
        <text class="risk-tag">过敏史校验</text>
        <text class="risk-tag">重复用药识别</text>
      </view>
    </view>

    <view class="save-btn" @click="saveMedicine">保存药品</view>
    </view>
  </view>
</template>

<script>
import { createMedicine } from '@/services/modules/medicine.service.js'

export default {
  data() {
    return {
      isSubmitting: false,
      medicine: { name: '', dose: '', stock: '', expire: '' }
    }
  },
  methods: {
    goBack() { uni.navigateBack() },
    async saveMedicine() {
      if (this.isSubmitting) return
      if (!this.medicine.name) {
        uni.showToast({ title: '请先填写药品名称', icon: 'none' })
        return
      }
      this.isSubmitting = true
      uni.showLoading({ title: '保存中' })
      try {
        await createMedicine({
          name: this.medicine.name.trim(),
          dose: this.medicine.dose.trim(),
          stock: Number(this.medicine.stock) || 0,
          expire: this.medicine.expire.trim(),
          risk: ''
        })
        uni.showToast({ title: '药品已保存', icon: 'success' })
        setTimeout(() => uni.navigateBack(), 500)
      } catch (error) {
        uni.showToast({ title: error?.message || '保存失败', icon: 'none' })
      } finally {
        this.isSubmitting = false
        uni.hideLoading()
      }
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

.form-card, .ai-card { padding: 32rpx; border-radius: 22rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 10rpx 24rpx rgba(31, 72, 55, 0.05); }
.card-title, .ai-title { display: block; font-size: 30rpx; color: #17231F; font-weight: 700; }
.form-item { margin-top: 24rpx; padding: 24rpx; border-radius: 14rpx; background: #F4F7F5; }.label { display: block; margin-bottom: 12rpx; color: #71817A; font-size: 24rpx; }input { font-size: 28rpx; color: #17231F; background: transparent; }
.ai-card { margin-top: 24rpx; background: #F0F7FA; border-color: #C9E3E8; }.ai-title { color: #187A83; }.ai-desc { display: block; margin-top: 12rpx; color: #50605A; font-size: 25rpx; line-height: 1.55; }.risk-tags { display: flex; flex-wrap: wrap; gap: 12rpx; margin-top: 20rpx; }.risk-tag { padding: 10rpx 16rpx; border-radius: 999rpx; background: #E8F3F6; color: #187A83; font-size: 22rpx; font-weight: 700; }
.save-btn { margin-top: 34rpx; width: 100%; height: 88rpx; display: flex; align-items: center; justify-content: center; border-radius: 14rpx; background: #0E9F8E; color: #FFFFFF; font-size: 30rpx; font-weight: 700; }
</style>

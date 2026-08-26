<template>
  <view class="page-container">
    <view class="header-card">
      <view>
        <text class="page-title">药品录入</text>
        <text class="page-desc">记录药品名称、剂量、库存和有效期，AI 会辅助检查风险。</text>
      </view>
      <view class="header-icon-wrap"><image class="header-icon" src="/static/icons/pill.png" mode="aspectFit" /></view>
    </view>

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

    <button class="save-btn" @click="saveMedicine">保存药品</button>
  </view>
</template>

<script>
export default {
  data() {
    return {
      medicine: { name: '', dose: '', stock: '', expire: '' }
    }
  },
  methods: {
    saveMedicine() {
      if (!this.medicine.name) {
        uni.showToast({ title: '请先填写药品名称', icon: 'none' })
        return
      }
      uni.showToast({ title: '药品已保存', icon: 'success' })
      setTimeout(() => uni.navigateBack(), 500)
    }
  }
}
</script>

<style scoped>
.page-container { min-height: 100vh; padding: 28rpx 28rpx 80rpx; background: linear-gradient(180deg, #EEFBF7 0%, #F8FAFC 34%, #F8FAFC 100%); box-sizing: border-box; }
.header-card { display: flex; justify-content: space-between; align-items: center; gap: 20rpx; padding: 36rpx; border-radius: 18rpx; color: #fff; background: linear-gradient(135deg, #0F766E, #10B981); box-shadow: 0 16rpx 36rpx rgba(13,148,136,.18); }
.page-title { display: block; font-size: 40rpx; font-weight: 900; }.page-desc { display: block; margin-top: 10rpx; font-size: 24rpx; line-height: 1.5; opacity: .9; }.header-icon-wrap { width: 86rpx; height: 86rpx; border-radius: 16rpx; background: rgba(255,255,255,.18); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }.header-icon { width: 48rpx; height: 48rpx; }
.form-card, .ai-card { margin-top: 24rpx; padding: 32rpx; border-radius: 16rpx; background: #fff; box-shadow: 0 8rpx 22rpx rgba(15,23,42,.05); }
.card-title, .ai-title { display: block; font-size: 31rpx; color: #1E293B; font-weight: 900; }
.form-item { margin-top: 24rpx; padding: 22rpx; border-radius: 14rpx; background: #F8FAFC; }.label { display: block; margin-bottom: 12rpx; color: #64748B; font-size: 24rpx; }input { font-size: 28rpx; color: #1E293B; }
.ai-card { background: linear-gradient(180deg, #FFFFFF, #ECFDF5); }.ai-title { color: #0F766E; }.ai-desc { display: block; margin-top: 12rpx; color: #334155; font-size: 25rpx; line-height: 1.55; }.risk-tags { display: flex; flex-wrap: wrap; gap: 12rpx; margin-top: 20rpx; }.risk-tag { padding: 9rpx 14rpx; border-radius: 999rpx; background: #D1FAE5; color: #059669; font-size: 22rpx; font-weight: 800; }
.save-btn { margin-top: 34rpx; width: 100%; height: 88rpx; line-height: 88rpx; border-radius: 14rpx; border: none; background: #0F766E; color: #fff; font-size: 30rpx; font-weight: 900; }
</style>

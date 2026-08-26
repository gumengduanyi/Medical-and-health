<template>
  <view class="page-container">
    <view class="user-card">
      <view class="avatar-wrap"><image class="avatar-img" src="/static/icons/user.png" mode="aspectFit" /></view>
      <view class="user-info"><text class="user-name">王先生</text><text class="user-desc">已接入 OCR 报告、药箱与 AI 健康建议</text></view>
    </view>

    <view class="stats-grid">
      <view class="stat-card"><text class="stat-value">12</text><text class="stat-label">报告入库</text></view>
      <view class="stat-card"><text class="stat-value">8</text><text class="stat-label">药品管理</text></view>
      <view class="stat-card"><text class="stat-value">3</text><text class="stat-label">风险提醒</text></view>
    </view>

    <view class="profile-health-card">
      <view>
        <text class="profile-title">账户资料完整度 72%</text>
        <text class="profile-desc">补全过敏史和家族史后，AI 用药建议会更稳妥。</text>
      </view>
      <button class="profile-btn" @click="goHealthInfo">完善</button>
    </view>

    <view class="shortcut-grid">
      <view class="shortcut-card" @click="goOcrScan"><image class="shortcut-icon" src="/static/icons/report.png" mode="aspectFit" /><text class="shortcut-title">报告识别</text></view>
      <view class="shortcut-card" @click="goMedicineForm"><image class="shortcut-icon" src="/static/icons/pill.png" mode="aspectFit" /><text class="shortcut-title">药品录入</text></view>
      <view class="shortcut-card" @click="goAiChat"><image class="shortcut-icon" src="/static/icons/sparkle.png" mode="aspectFit" /><text class="shortcut-title">AI 问答</text></view>
    </view>

    <view class="menu-card">
      <view class="menu-item" v-for="item in menus" :key="item.title" @click="handleMenu(item)">
        <view class="menu-icon-wrap" :class="item.theme">
          <image v-if="item.icon" class="menu-icon" :src="item.icon" mode="aspectFit" />
          <text v-else class="menu-emoji">{{ item.emoji }}</text>
        </view>
        <view class="menu-body"><text class="menu-title">{{ item.title }}</text><text class="menu-desc">{{ item.desc }}</text></view>
        <image class="arrow" src="/static/icons/arrow-right.png" mode="aspectFit" />
      </view>
    </view>

    <view class="privacy-card"><text class="privacy-title">数据安全</text><text class="privacy-text">健康资料仅用于本地展示和后续接口联调。正式接入 AI 前建议补充授权、脱敏与数据留存策略。</text></view>
    <FloatingAction />
  </view>
</template>

<script>
import FloatingAction from '@/components/FloatingAction/FloatingAction.vue'
import { smoothNavigateTo } from '@/utils/router.js'

export default {
  components: { FloatingAction },
  data() {
    return {
      menus: [
        { title: '个人健康信息', desc: '身高体重、病史、过敏史与 AI 个性化依据', icon: '/static/icons/profile.png', theme: 'green', route: '/pages-sub/healthInfo/healthInfo' },
        { title: 'OCR 报告识别', desc: '识别体检报告、诊断证明和化验单', icon: '/static/icons/report.png', theme: 'blue', route: '/pages-sub/ocr_scan/ocr_scan' },
        { title: '药品录入管理', desc: '新增药品、维护库存和有效期', icon: '/static/icons/pill.png', theme: 'green', route: '/pages-sub/medicine_form/medicine_form' },
        { title: 'AI 健康问答', desc: '询问报告指标、用药注意和复诊建议', icon: '/static/icons/sparkle.png', theme: 'purple', route: '/pages-sub/ai_chat/ai_chat' },
        { title: '扫码拍照上传', desc: '生成二维码，用手机拍摄并上传健康资料', icon: '/static/icons/plus.png', theme: 'blue', route: '/pages/scan_upload/scan_upload' },
        { title: '亲人健康管理', desc: '为家人建立独立档案并查看风险提醒', icon: '/static/icons/family.png', theme: 'amber' },
        { title: '帮助与反馈', desc: '查看使用说明，反馈 OCR 或 AI 建议问题', icon: '/static/icons/help.png', theme: 'gray' }
      ]
    }
  },
  methods: {
    goHealthInfo() { smoothNavigateTo('/pages-sub/healthInfo/healthInfo') },
    goOcrScan() { smoothNavigateTo('/pages-sub/ocr_scan/ocr_scan') },
    goMedicineForm() { smoothNavigateTo('/pages-sub/medicine_form/medicine_form') },
    goAiChat() { smoothNavigateTo('/pages-sub/ai_chat/ai_chat') },
    handleMenu(item) {
      if (item.route) { smoothNavigateTo(item.route); return }
      uni.showToast({ title: '功能规划中', icon: 'none' })
    }
  }
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: linear-gradient(180deg, #EEFBF7 0%, #F8FAFC 34%, #F8FAFC 100%); padding: 28rpx 28rpx 170rpx; box-sizing: border-box; }.user-card { display: flex; align-items: center; gap: 24rpx; padding: 36rpx; border-radius: 18rpx; background: linear-gradient(135deg, #0F766E, #10B981); color: #fff; box-shadow: 0 16rpx 36rpx rgba(13,148,136,.18); }
.avatar-wrap { width: 116rpx; height: 116rpx; border-radius: 50%; background: rgba(255,255,255,.92); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }.avatar-img { width: 68rpx; height: 68rpx; }.user-info { flex: 1; }.user-name { display: block; font-size: 40rpx; font-weight: 900; }.user-desc { display: block; margin-top: 10rpx; font-size: 24rpx; line-height: 1.45; opacity: .88; }
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx; margin: 24rpx 0; }.stat-card { padding: 24rpx 12rpx; border-radius: 16rpx; background: #fff; text-align: center; box-shadow: 0 8rpx 22rpx rgba(15,23,42,.05); }.stat-value { display: block; font-size: 36rpx; color: #0F766E; font-weight: 900; }.stat-label { display: block; margin-top: 8rpx; font-size: 22rpx; color: #64748B; }
.profile-health-card { display: flex; align-items: center; justify-content: space-between; gap: 20rpx; margin-bottom: 24rpx; padding: 28rpx; border-radius: 16rpx; background: #fff; box-shadow: 0 8rpx 22rpx rgba(15,23,42,.05); }
.profile-title { display: block; font-size: 29rpx; color: #1E293B; font-weight: 900; }.profile-desc { display: block; margin-top: 8rpx; font-size: 23rpx; color: #64748B; line-height: 1.45; }.profile-btn { flex-shrink: 0; margin: 0; width: 112rpx; height: 64rpx; line-height: 64rpx; border-radius: 999rpx; background: #10B981; color: #fff; border: none; font-size: 25rpx; }
.shortcut-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx; margin-bottom: 24rpx; }.shortcut-card { padding: 24rpx 12rpx; border-radius: 16rpx; background: #fff; text-align: center; box-shadow: 0 8rpx 22rpx rgba(15,23,42,.05); border: 1rpx solid #EEF2F7; }.shortcut-icon { display: block; width: 38rpx; height: 38rpx; margin: 0 auto; }.shortcut-title { display: block; margin-top: 10rpx; color: #1E293B; font-size: 24rpx; font-weight: 900; }
.menu-card, .privacy-card { margin-top: 24rpx; border-radius: 16rpx; background: #fff; box-shadow: 0 8rpx 22rpx rgba(15,23,42,.05); overflow: hidden; }.menu-item { display: flex; align-items: center; gap: 20rpx; padding: 28rpx; border-bottom: 1rpx solid #F1F5F9; }.menu-item:last-child { border-bottom: none; }
.menu-icon-wrap { width: 72rpx; height: 72rpx; border-radius: 16rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }.menu-icon-wrap.green { background: #ECFDF5; }.menu-icon-wrap.blue { background: #EFF6FF; }.menu-icon-wrap.purple { background: #EEF2FF; }.menu-icon-wrap.amber { background: #FFFBEB; }.menu-icon-wrap.gray { background: #F1F5F9; }.menu-icon { width: 38rpx; height: 38rpx; }.menu-emoji { font-size: 34rpx; }.menu-body { flex: 1; min-width: 0; }.menu-title { display: block; font-size: 29rpx; color: #1E293B; font-weight: 900; }.menu-desc { display: block; margin-top: 8rpx; font-size: 23rpx; line-height: 1.45; color: #64748B; }.arrow { width: 24rpx; height: 24rpx; }
.privacy-card { padding: 30rpx; background: linear-gradient(180deg, #FFFFFF, #F0FDFA); }.privacy-title { display: block; font-size: 30rpx; color: #0F766E; font-weight: 900; }.privacy-text { display: block; margin-top: 12rpx; font-size: 25rpx; color: #334155; line-height: 1.6; }
</style>

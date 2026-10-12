<template>
  <view class="page-container">
    <view class="custom-nav">
      <view class="status-bar"></view>
      <view class="nav-content">
        <text class="nav-title">我的</text>
      </view>
    </view>
    
    <view class="page-content">
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
      <view class="shortcut-card" @click="goOcrScan"><image class="shortcut-icon" src="/static/icons/report.png" mode="aspectFit" /><text class="shortcut-title">档案识别</text></view>
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

    <FloatingAction />
    </view>
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
        { title: '档案 OCR 识别', desc: '识别体检报告、诊断证明和化验单', icon: '/static/icons/report.png', theme: 'blue', route: '/pages-sub/ocr_scan/ocr_scan' },
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
.page-container { min-height: 100vh; background: #F4F7F5; }
.custom-nav { position: fixed; top: 0; left: 0; right: 0; z-index: 999; background: rgba(244, 247, 245, 0.92); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-bottom: 1rpx solid #DDE7E1; }
.status-bar { height: var(--status-bar-height); }
.nav-content { height: 100rpx; padding: 0 32rpx; display: flex; align-items: center; justify-content: center; position: relative; }
.nav-title { position: absolute; left: 50%; transform: translateX(-50%); font-size: 36rpx; font-weight: 700; color: #17231F; }
.nav-actions { display: flex; gap: 20rpx; align-items: center; }
.nav-icon { width: 68rpx; height: 68rpx; border-radius: 50%; background: rgba(56, 189, 248, 0.12); display: flex; align-items: center; justify-content: center; font-size: 32rpx; border: 1rpx solid rgba(56, 189, 248, 0.2); }
.page-content { padding: 32rpx; padding-top: calc(var(--status-bar-height) + 100rpx + 16rpx); padding-bottom: 170rpx; }
.user-card { display: flex; align-items: center; gap: 28rpx; padding: 40rpx; border-radius: 24rpx; background: #FFFFFF; color: #17231F; box-shadow: 0 12rpx 28rpx rgba(31, 72, 55, 0.06); border: 1rpx solid #DDE7E1; }
.avatar-wrap { width: 120rpx; height: 120rpx; border-radius: 50%; background: #E1F3ED; display: flex; align-items: center; justify-content: center; flex-shrink: 0; border: 2rpx solid #BFE3D6; }.avatar-img { width: 72rpx; height: 72rpx; }.user-info { flex: 1; }.user-name { display: block; font-size: 44rpx; font-weight: 700; }.user-desc { display: block; margin-top: 12rpx; font-size: 26rpx; line-height: 1.5; color: #71817A; }
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx; margin: 32rpx 0; }.stat-card { padding: 28rpx 16rpx; border-radius: 18rpx; background: #FFFFFF; text-align: center; border: 1rpx solid #DDE7E1; }.stat-value { display: block; font-size: 40rpx; color: #0E9F8E; font-weight: 700; }.stat-label { display: block; margin-top: 10rpx; font-size: 24rpx; color: #71817A; }
.profile-health-card { display: flex; align-items: center; justify-content: space-between; gap: 24rpx; margin-bottom: 32rpx; padding: 32rpx; border-radius: 20rpx; background: #F0FAF6; border: 1rpx solid #BFE3D6; }
.profile-title { display: block; font-size: 30rpx; color: #17231F; font-weight: 700; }.profile-desc { display: block; margin-top: 10rpx; font-size: 24rpx; color: #71817A; line-height: 1.5; }.profile-btn { flex-shrink: 0; margin: 0; width: 120rpx; height: 68rpx; line-height: 68rpx; border-radius: 14rpx; background: #0E9F8E; color: #FFFFFF; border: none; font-size: 26rpx; font-weight: 700; }
.shortcut-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx; margin-bottom: 32rpx; }.shortcut-card { padding: 28rpx 16rpx; border-radius: 18rpx; background: #FFFFFF; text-align: center; border: 1rpx solid #DDE7E1; }.shortcut-icon { display: block; width: 40rpx; height: 40rpx; margin: 0 auto; }.shortcut-title { display: block; margin-top: 12rpx; color: #17231F; font-size: 24rpx; font-weight: 600; }
.menu-card { margin-top: 32rpx; border-radius: 22rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; overflow: hidden; box-shadow: 0 10rpx 24rpx rgba(31, 72, 55, 0.05); }.menu-item { display: flex; align-items: center; gap: 24rpx; padding: 32rpx; border-bottom: 1rpx solid #E8F1ED; }.menu-item:last-child { border-bottom: none; }
.menu-icon-wrap { width: 76rpx; height: 76rpx; border-radius: 16rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }.menu-icon-wrap.green { background: #E1F3ED; }.menu-icon-wrap.blue { background: #E8F3F6; }.menu-icon-wrap.purple { background: #F0ECFA; }.menu-icon-wrap.amber { background: #FFF0DF; }.menu-icon-wrap.gray { background: #EEF2F0; }.menu-icon { width: 40rpx; height: 40rpx; }.menu-emoji { font-size: 36rpx; }.menu-body { flex: 1; min-width: 0; }.menu-title { display: block; font-size: 30rpx; color: #17231F; font-weight: 700; }.menu-desc { display: block; margin-top: 10rpx; font-size: 24rpx; line-height: 1.5; color: #71817A; }.arrow { width: 24rpx; height: 24rpx; opacity: 0.5; }
</style>

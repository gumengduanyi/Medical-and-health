<template>
  <view class="page-container">
    <view class="custom-nav">
      <view class="status-bar"></view>
      <view class="nav-content">
        <text class="nav-title">我的</text>
      </view>
    </view>
    
    <view class="page-content">
      <view class="profile-hero">
        <view class="hero-topline"><text class="hero-kicker">HEALTH SPACE</text><text class="hero-status">资料已同步</text></view>
        <view class="hero-main">
          <view class="avatar-wrap"><image class="avatar-img" src="/static/icons/user.png" mode="aspectFit" /></view>
          <view class="user-info"><text class="user-name">王先生</text><text class="user-desc">你的健康资料都在这里</text></view>
          <view class="profile-mark"><text>72</text><text>%</text></view>
        </view>
        <view class="hero-bottom"><text>健康资料完整度</text><text>补全资料，让建议更贴合</text></view>
        <view class="progress-track"><view class="progress-value"></view></view>
      </view>

      <view class="stats-strip">
        <view class="stat-item"><text class="stat-value">12</text><text class="stat-label">报告入库</text></view>
        <view class="stat-divider"></view>
        <view class="stat-item"><text class="stat-value">8</text><text class="stat-label">药品管理</text></view>
        <view class="stat-divider"></view>
        <view class="stat-item"><text class="stat-value warning">3</text><text class="stat-label">风险提醒</text></view>
      </view>

      <view class="section-heading"><view><text class="section-eyebrow">QUICK ACCESS</text><text class="section-title">常用工具</text></view><text class="section-caption">快速开始</text></view>
      <view class="shortcut-grid">
        <view class="shortcut-card shortcut-report" @click="goOcrScan"><view class="shortcut-icon-wrap"><image class="shortcut-icon" src="/static/icons/report.png" mode="aspectFit" /></view><text class="shortcut-title">档案识别</text><text class="shortcut-desc">报告与指标</text></view>
        <view class="shortcut-card shortcut-medicine" @click="goMedicineForm"><view class="shortcut-icon-wrap"><image class="shortcut-icon" src="/static/icons/pill.png" mode="aspectFit" /></view><text class="shortcut-title">药品录入</text><text class="shortcut-desc">管理药箱</text></view>
        <view class="shortcut-card shortcut-ai" @click="goAiChat"><view class="shortcut-icon-wrap"><image class="shortcut-icon" src="/static/icons/sparkle.png" mode="aspectFit" /></view><text class="shortcut-title">AI 问答</text><text class="shortcut-desc">获得健康建议</text></view>
      </view>

      <view class="completion-row" @click="goHealthInfo"><view class="completion-icon"><image src="/static/icons/profile.png" mode="aspectFit" /></view><view class="completion-copy"><text class="completion-title">完善个人健康信息</text><text class="completion-desc">补全过敏史和家族史，减少用药风险</text></view><view class="completion-action">完善 <text>›</text></view></view>

      <view class="section-heading menu-heading"><view><text class="section-eyebrow">MORE</text><text class="section-title">更多管理</text></view></view>
      <view class="menu-list">
        <view class="menu-item" v-for="item in menus" :key="item.title" @click="handleMenu(item)">
          <view class="menu-icon-wrap" :class="item.theme"><image v-if="item.icon" class="menu-icon" :src="item.icon" mode="aspectFit" /><text v-else class="menu-emoji">{{ item.emoji }}</text></view>
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
        { title: '档案智能识别', desc: '识别体检报告、诊断证明和化验单', icon: '/static/icons/report.png', theme: 'blue', route: '/pages-sub/ocr_scan/ocr_scan' },
        { title: '药品录入管理', desc: '新增药品、维护库存和有效期', icon: '/static/icons/pill.png', theme: 'green', route: '/pages-sub/medicine_form/medicine_form' },
        { title: 'AI 健康问答', desc: '询问报告指标、用药注意和复诊建议', icon: '/static/icons/sparkle.png', theme: 'purple', route: '/pages-sub/ai_chat/ai_chat' },
        { title: '扫码拍照上传', desc: '生成二维码，用手机拍摄并上传健康资料', icon: '/static/icons/plus.png', theme: 'blue', route: '/pages/scan_upload/scan_upload' },
        { title: '亲人健康管理', desc: '为家人建立独立档案并查看风险提醒', icon: '/static/icons/family.png', theme: 'amber' },
        { title: '帮助与反馈', desc: '查看使用说明，反馈报告识别或 AI 建议问题', icon: '/static/icons/help.png', theme: 'gray' }
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
.page-content { padding: 28rpx; padding-top: calc(var(--status-bar-height) + 100rpx + 20rpx); padding-bottom: 170rpx; }
.profile-hero { padding: 32rpx; border-radius: 28rpx; color: #F8FFFC; background: #173F35; box-shadow: 0 18rpx 36rpx rgba(23, 63, 53, 0.2); }.hero-topline, .hero-bottom { display: flex; align-items: center; justify-content: space-between; }.hero-kicker { color: #96D8BF; font-size: 21rpx; letter-spacing: 3rpx; font-weight: 700; }.hero-status { padding: 8rpx 14rpx; border-radius: 999rpx; background: rgba(224, 255, 239, 0.13); color: #C1F0DC; font-size: 21rpx; }.hero-main { display: flex; align-items: center; gap: 22rpx; margin-top: 40rpx; }.avatar-wrap { width: 112rpx; height: 112rpx; border-radius: 50%; background: #E1F3ED; display: flex; align-items: center; justify-content: center; flex-shrink: 0; border: 5rpx solid rgba(255, 255, 255, 0.24); }.avatar-img { width: 68rpx; height: 68rpx; }.user-info { flex: 1; }.user-name { display: block; font-size: 42rpx; font-weight: 700; }.user-desc { display: block; margin-top: 10rpx; font-size: 24rpx; color: #B4D4C8; }.profile-mark { width: 94rpx; height: 94rpx; display: flex; align-items: baseline; justify-content: center; color: #F4C86A; border: 2rpx solid rgba(244, 200, 106, 0.65); border-radius: 50%; }.profile-mark text:first-child { font-size: 34rpx; font-weight: 700; }.profile-mark text:last-child { font-size: 20rpx; }.hero-bottom { margin-top: 36rpx; color: #D7E9E2; font-size: 23rpx; }.hero-bottom text:last-child { color: #9BCBB9; }.progress-track { height: 10rpx; margin-top: 16rpx; border-radius: 999rpx; background: rgba(255, 255, 255, 0.14); overflow: hidden; }.progress-value { width: 72%; height: 100%; border-radius: inherit; background: #F4C86A; }
.stats-strip { display: flex; align-items: center; justify-content: space-around; margin: 22rpx 0 38rpx; padding: 24rpx 12rpx; border-radius: 20rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 8rpx 20rpx rgba(31, 72, 55, 0.04); }.stat-item { flex: 1; text-align: center; }.stat-value { display: block; font-size: 38rpx; color: #0E9F8E; font-weight: 700; }.stat-value.warning { color: #C97931; }.stat-label { display: block; margin-top: 8rpx; font-size: 22rpx; color: #71817A; }.stat-divider { width: 1rpx; height: 48rpx; background: #E4ECE8; }
.section-heading { display: flex; align-items: end; justify-content: space-between; margin: 0 4rpx 18rpx; }.section-eyebrow { display: block; color: #0E9F8E; font-size: 19rpx; letter-spacing: 2rpx; font-weight: 700; }.section-title { display: block; margin-top: 6rpx; color: #17231F; font-size: 32rpx; font-weight: 700; }.section-caption { color: #9AA9A3; font-size: 23rpx; }.shortcut-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14rpx; }.shortcut-card { min-height: 196rpx; padding: 22rpx 12rpx; border-radius: 20rpx; text-align: center; border: 1rpx solid transparent; }.shortcut-report { background: #EAF7F2; border-color: #CDEBDD; }.shortcut-medicine { background: #FFF4DF; border-color: #F4DEB5; }.shortcut-ai { background: #EFF0FB; border-color: #DCDCF2; }.shortcut-icon-wrap { width: 64rpx; height: 64rpx; margin: 0 auto 16rpx; display: flex; align-items: center; justify-content: center; border-radius: 18rpx; background: rgba(255, 255, 255, 0.72); }.shortcut-icon { width: 38rpx; height: 38rpx; }.shortcut-title { display: block; color: #17231F; font-size: 26rpx; font-weight: 700; }.shortcut-desc { display: block; margin-top: 8rpx; color: #6F8078; font-size: 20rpx; }
.completion-row { display: flex; align-items: center; gap: 18rpx; margin: 34rpx 0 40rpx; padding: 24rpx; border-radius: 20rpx; background: #FFF9ED; border: 1rpx solid #F2E0B6; }.completion-icon { width: 62rpx; height: 62rpx; display: flex; align-items: center; justify-content: center; border-radius: 16rpx; background: #F7D783; }.completion-icon image { width: 36rpx; height: 36rpx; }.completion-copy { flex: 1; min-width: 0; }.completion-title { display: block; color: #493B20; font-size: 27rpx; font-weight: 700; }.completion-desc { display: block; margin-top: 7rpx; color: #8D7B54; font-size: 21rpx; line-height: 1.4; }.completion-action { color: #A36C1F; font-size: 23rpx; font-weight: 700; }.completion-action text { margin-left: 5rpx; font-size: 32rpx; font-weight: 400; }
.menu-heading { margin-bottom: 18rpx; }.menu-list { border-radius: 22rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; overflow: hidden; box-shadow: 0 10rpx 24rpx rgba(31, 72, 55, 0.05); }.menu-item { display: flex; align-items: center; gap: 20rpx; padding: 24rpx; border-bottom: 1rpx solid #E8F1ED; }.menu-item:last-child { border-bottom: none; }
.menu-icon-wrap { width: 76rpx; height: 76rpx; border-radius: 16rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }.menu-icon-wrap.green { background: #E1F3ED; }.menu-icon-wrap.blue { background: #E8F3F6; }.menu-icon-wrap.purple { background: #F0ECFA; }.menu-icon-wrap.amber { background: #FFF0DF; }.menu-icon-wrap.gray { background: #EEF2F0; }.menu-icon { width: 40rpx; height: 40rpx; }.menu-emoji { font-size: 36rpx; }.menu-body { flex: 1; min-width: 0; }.menu-title { display: block; font-size: 30rpx; color: #17231F; font-weight: 700; }.menu-desc { display: block; margin-top: 10rpx; font-size: 24rpx; line-height: 1.5; color: #71817A; }.arrow { width: 24rpx; height: 24rpx; opacity: 0.5; }
</style>

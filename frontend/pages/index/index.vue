<template>
  <view class="page-container">
    <view class="custom-nav">
      <view class="status-bar"></view>
      <view class="nav-content">
        <view class="notification-trigger" @click="toggleNotifications">
          <view class="notification-ring"></view>
          <view v-if="notificationCount" class="notification-badge">{{ notificationCount }}</view>
        </view>
        <text class="nav-title">健康助手</text>
        <view class="nav-placeholder"></view>
      </view>
    </view>
    
    <view class="page-content">
    <view v-if="notificationsOpen" class="notification-panel">
      <view class="notification-panel-head">
        <view>
          <text class="notification-panel-title">通知与待办</text>
            <text class="notification-panel-subtitle">{{ pendingCount ? `还有 ${pendingCount} 项健康事项待处理` : '当前没有待处理事项' }}</text>
        </view>
          <view class="notification-head-actions">
            <text v-if="pendingCount" class="notification-clear" @click="completeAllNotifications">全部完成</text>
            <text class="notification-close" @click="toggleNotifications">×</text>
          </view>
      </view>
      <view class="notification-list">
          <view v-if="!activeNotifications.length" class="notification-empty">
            <text class="notification-empty-icon">✓</text>
            <text class="notification-empty-title">今天安排得很好</text>
            <text class="notification-empty-desc">新的健康提醒会出现在这里</text>
          </view>
          <view class="notification-item" v-for="item in activeNotifications" :key="item.id" :class="{ unread: !item.read }" @click="handleNotification(item)">
          <view class="notification-dot" :class="item.theme"></view>
          <view class="notification-copy">
              <view class="notification-title-row"><text class="notification-title">{{ item.title }}</text><text class="notification-kind">{{ item.kind === 'todo' ? '待办' : '提醒' }}</text></view>
              <text class="notification-desc">{{ item.desc }}</text>
          </view>
            <view class="notification-action" @click.stop="completeNotification(item)">{{ item.kind === 'todo' ? '完成' : '知道了' }}</view>
            <image class="notification-arrow" src="/static/icons/arrow-right.png" mode="aspectFit" />
        </view>
      </view>
    </view>

    <view class="dashboard-hero">
      <view class="hero-copy">
        <text class="greet-date">{{ todayLabel }} · 智能健康管家</text>
        <text class="greet-title">早安，王先生</text>
        <text class="hero-summary">今天也要照顾好自己，先看看你的健康安排。</text>
      </view>
      <view class="greet-score">
        <text class="greet-score-value">82</text>
        <text class="greet-score-label">健康评分</text>
      </view>
    </view>

    <view class="today-focus" @click="toggleNotifications">
      <view class="focus-icon"><text>!</text></view>
      <view class="focus-copy"><text class="focus-title">今天有 {{ pendingCount }} 项事项需要关注</text><text class="focus-desc">报告确认、药品库存和健康资料都可以在这里处理</text></view>
      <text class="focus-arrow">›</text>
    </view>

    <view class="section-head overview-head"><view><text class="section-kicker">TODAY</text><text class="section-title">健康概览</text></view><text class="section-link" @click="goRecord">查看全部</text></view>
    <view class="metric-strip">
      <view class="metric-item"><text class="metric-value">128<text class="metric-unit">/ 82</text></text><text class="metric-label">血压 mmHg</text><text class="metric-status">最近一次</text></view>
      <view class="metric-item"><text class="metric-value">72</text><text class="metric-label">心率 bpm</text><text class="metric-status good">状态稳定</text></view>
      <view class="metric-item"><text class="metric-value">6.1</text><text class="metric-label">血糖 mmol/L</text><text class="metric-status">最近一次</text></view>
    </view>

    <view class="trend-card">
      <view class="section-head compact">
        <text class="section-title">近 7 天血压趋势</text>
        <text class="section-link" @click="goRecord">查看详情</text>
      </view>
      <view class="trend-chart">
        <view class="trend-bar" v-for="item in pressureTrend" :key="item.day">
          <view class="trend-track"><view class="trend-fill" :style="{ height: item.value + '%' }"></view></view>
          <text class="trend-label">{{ item.day }}</text>
        </view>
      </view>
    </view>

    <view class="section-head quick-head">
      <view><text class="section-kicker">TOOLS</text><text class="section-title">常用功能</text></view>
      <text class="section-link" @click="goChat">问 AI</text>
    </view>
    <view class="quick-grid">
      <view class="quick-card" v-for="item in quickActions" :key="item.title" :class="item.theme" @click="handleQuickAction(item.action)">
        <view class="quick-icon-wrap">
          <image class="quick-icon" :src="item.icon" mode="aspectFit" />
        </view>
        <text class="quick-title">{{ item.title }}</text>
        <text class="quick-desc">{{ item.desc }}</text>
      </view>
    </view>

    <FloatingAction />
    </view>
  </view>
</template>

<script>
import FloatingAction from '@/components/FloatingAction/FloatingAction.vue'
import { smoothNavigateTo, smoothSwitchTab } from '@/utils/router.js'
import { getStorage, setStorage } from '@/store/storage.js'

const NOTIFICATION_STATE_KEY = 'health_notification_state'

export default {
  components: { FloatingAction },
  onShow() {
    this.restoreNotificationState()
  },
  data() {
    return {
      pressureTrend: [
        { day: '一', value: 62 }, { day: '二', value: 68 }, { day: '三', value: 74 },
        { day: '四', value: 71 }, { day: '五', value: 82 }, { day: '六', value: 78 }, { day: '日', value: 86 }
      ],
      quickActions: [
        { icon: '/static/icons/report.png', title: '智能识别', desc: '体检/诊断/药盒', theme: 'mint', action: 'ocr' },
        { icon: '/static/icons/record.png', title: '健康趋势', desc: '指标变化与异常', theme: 'blue', action: 'record' },
        { icon: '/static/icons/pill.png', title: '药品管理', desc: '库存/有效期/提醒', theme: 'amber', action: 'medication' },
        { icon: '/static/icons/profile.png', title: '健康信息', desc: '病史与过敏史', theme: 'gray', action: 'profile' }
      ],
      notificationsOpen: false,
      notifications: [
        { id: 'report', title: '体检报告待确认', desc: '血压、血糖、血脂 12 项指标待确认', route: '/pages/report_library/report_library', theme: 'blue', kind: 'todo', read: false, completed: false },
        { id: 'medicine-stock', title: '药品库存与有效期提醒', desc: '1 种药品库存偏低，1 种药品即将过期，建议优先处理', route: '/pages/medication/medication', theme: 'green', kind: 'todo', read: false, completed: false },
        { id: 'medicine-ai', title: 'AI 用药提醒', desc: '阿司匹林存在低库存风险，建议 3 天内补货；请按医嘱监测血压', route: '/pages/medication/medication', theme: 'green', kind: 'alert', read: false, completed: false },
        { id: 'profile', title: '健康资料待完善', desc: '补全过敏史和病史，让 AI 提醒更准确', route: '/pages-sub/healthInfo/healthInfo', theme: 'amber', kind: 'todo', read: false, completed: false },
        { id: 'pressure', title: 'AI 异常指标预警', desc: '血压连续偏高，建议低盐饮食、规律作息并每日固定时段监测', route: '/pages/health_records/health_records', theme: 'red', kind: 'alert', read: false, completed: false }
      ]
    }
  },
  computed: {
    activeNotifications() {
      return this.notifications.filter((item) => !item.completed)
    },
    notificationCount() {
      return this.notifications.filter((item) => !item.read && !item.completed).length
    },
    pendingCount() {
      return this.activeNotifications.length
    }
  },
  methods: {
    restoreNotificationState() {
      const state = getStorage(NOTIFICATION_STATE_KEY, {})
      this.notifications = this.notifications.map((item) => ({
        ...item,
        read: Boolean(state[item.id]?.read),
        completed: Boolean(state[item.id]?.completed)
      }))
    },
    saveNotificationState() {
      const state = this.notifications.reduce((result, item) => {
        result[item.id] = { read: item.read, completed: item.completed }
        return result
      }, {})
      setStorage(NOTIFICATION_STATE_KEY, state)
    },
    toggleNotifications() {
      this.notificationsOpen = !this.notificationsOpen
    },
    goMedication() {
      smoothSwitchTab('/pages/medication/medication')
    },
    goRecord() {
      smoothSwitchTab('/pages/health_records/health_records')
    },
    goAdd() {
      smoothNavigateTo('/pages-sub/ocr_scan/ocr_scan')
    },
    goChat() {
      smoothNavigateTo('/pages-sub/ai_chat/ai_chat')
    },
    goHealthInfo() {
      smoothNavigateTo('/pages-sub/healthInfo/healthInfo')
    },
    handleQuickAction(action) {
      const handlers = {
        ocr: this.goAdd,
        record: this.goRecord,
        medication: this.goMedication,
        profile: this.goHealthInfo
      }
      if (handlers[action]) handlers[action]()
    },
    handleNotification(item) {
      item.read = true
      this.saveNotificationState()
      this.notificationsOpen = false
      if (item.route === '/pages/medication/medication' || item.route === '/pages/health_records/health_records') {
        smoothSwitchTab(item.route)
        return
      }
      smoothNavigateTo(item.route)
    },
    completeNotification(item) {
      item.read = true
      item.completed = true
      this.saveNotificationState()
      uni.showToast({ title: '已完成', icon: 'success' })
    },
    completeAllNotifications() {
      this.notifications.forEach((item) => {
        item.read = true
        item.completed = true
      })
      this.saveNotificationState()
      uni.showToast({ title: '待办已全部完成', icon: 'success' })
    }
  }
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: #F4F7F5; }
.custom-nav { position: fixed; top: 0; left: 0; right: 0; z-index: 999; background: rgba(244, 247, 245, 0.94); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-bottom: 1rpx solid #DDE7E1; }
.status-bar { height: var(--status-bar-height); }
.nav-content { height: 100rpx; padding: 0 32rpx; display: flex; align-items: center; justify-content: space-between; position: relative; }
.nav-title { position: absolute; left: 50%; transform: translateX(-50%); font-size: 36rpx; font-weight: 700; color: #17231F; }
.nav-placeholder { width: 68rpx; height: 68rpx; }
.notification-trigger { position: relative; z-index: 1001; width: 64rpx; height: 64rpx; border-radius: 50%; background: #FFFFFF; border: 1rpx solid #DDE7E1; display: flex; align-items: center; justify-content: center; box-shadow: 0 8rpx 20rpx rgba(31, 72, 55, 0.08); }
.notification-ring { width: 24rpx; height: 27rpx; border: 3rpx solid #0E9F8E; border-radius: 14rpx 14rpx 9rpx 9rpx; position: relative; box-sizing: border-box; }
.notification-ring::before { content: ''; position: absolute; left: 50%; bottom: -8rpx; width: 9rpx; height: 5rpx; border-radius: 0 0 8rpx 8rpx; background: #0E9F8E; transform: translateX(-50%); }
.notification-ring::after { content: ''; position: absolute; left: 50%; top: -7rpx; width: 8rpx; height: 7rpx; border: 3rpx solid #0E9F8E; border-bottom: 0; border-radius: 8rpx 8rpx 0 0; transform: translateX(-50%); box-sizing: border-box; }
.notification-badge { position: absolute; top: -8rpx; right: -8rpx; min-width: 30rpx; height: 30rpx; padding: 0 7rpx; box-sizing: border-box; border-radius: 999rpx; background: #E85D4A; color: #FFFFFF; font-size: 18rpx; line-height: 30rpx; text-align: center; border: 3rpx solid #F4F7F5; }
.nav-actions { display: flex; gap: 20rpx; align-items: center; }
.nav-icon { width: 68rpx; height: 68rpx; border-radius: 50%; background: rgba(56, 189, 248, 0.12); display: flex; align-items: center; justify-content: center; font-size: 32rpx; border: 1rpx solid rgba(56, 189, 248, 0.2); }
.page-content { padding: 32rpx; padding-top: calc(var(--status-bar-height) + 100rpx + 24rpx); padding-bottom: 170rpx; }
.notification-panel { position: fixed; z-index: 10000; top: calc(var(--status-bar-height) + 104rpx); left: 24rpx; right: 24rpx; max-height: 70vh; overflow-y: auto; padding: 24rpx 28rpx; border-radius: 18rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 12rpx 28rpx rgba(31, 72, 55, 0.12); }
.notification-panel-head { display: flex; align-items: flex-start; justify-content: space-between; }
.notification-head-actions { display: flex; align-items: center; gap: 14rpx; }
.notification-panel-title { display: block; font-size: 32rpx; font-weight: 700; color: #17231F; }
.notification-panel-subtitle { display: block; margin-top: 8rpx; font-size: 23rpx; color: #71817A; }
.notification-clear { padding: 8rpx 12rpx; color: #0E9F8E; font-size: 22rpx; font-weight: 600; }
.notification-close { width: 48rpx; height: 48rpx; color: #71817A; font-size: 42rpx; font-weight: 300; line-height: 42rpx; text-align: center; }
.notification-list { margin-top: 20rpx; }
.notification-item { display: flex; align-items: center; gap: 16rpx; padding: 20rpx 0; border-top: 1rpx solid #E8F1ED; }
.notification-item:first-child { border-top: none; }
.notification-item:not(.unread) { opacity: 0.72; }
.notification-dot { width: 16rpx; height: 16rpx; border-radius: 50%; flex-shrink: 0; background: #0E9F8E; }
.notification-dot.blue { background: #3284A8; }.notification-dot.green { background: #0E9F8E; }.notification-dot.amber { background: #E58A3A; }.notification-dot.red { background: #E85D4A; }
.notification-copy { flex: 1; min-width: 0; }
.notification-title-row { display: flex; align-items: center; gap: 10rpx; }
.notification-title { display: block; font-size: 27rpx; font-weight: 600; color: #17231F; }
.notification-kind { flex-shrink: 0; padding: 4rpx 8rpx; border-radius: 6rpx; background: #E1F3ED; color: #0E9F8E; font-size: 18rpx; }
.notification-desc { display: block; margin-top: 6rpx; font-size: 23rpx; line-height: 1.4; color: #71817A; }
.notification-action { flex-shrink: 0; color: #0E9F8E; font-size: 21rpx; font-weight: 600; }
.notification-arrow { width: 22rpx; height: 22rpx; opacity: 0.45; flex-shrink: 0; }
.notification-empty { display: flex; flex-direction: column; align-items: center; padding: 36rpx 0 24rpx; }
.notification-empty-icon { width: 58rpx; height: 58rpx; border-radius: 50%; background: #E1F3ED; color: #0E9F8E; font-size: 34rpx; line-height: 58rpx; text-align: center; }
.notification-empty-title { margin-top: 16rpx; color: #17231F; font-size: 27rpx; font-weight: 700; }
.notification-empty-desc { margin-top: 8rpx; color: #71817A; font-size: 22rpx; }
.dashboard-hero { display: flex; align-items: center; justify-content: space-between; padding: 34rpx 30rpx; border-radius: 26rpx; background: #173F35; color: #F8FFFC; box-shadow: 0 16rpx 32rpx rgba(23, 63, 53, 0.18); }
.hero-copy { flex: 1; min-width: 0; padding-right: 20rpx; }
.greet-date { display: block; font-size: 24rpx; color: #71817A; }
.dashboard-hero .greet-date { color: #9BCBB9; }
.greet-title { display: block; margin-top: 10rpx; font-size: 40rpx; font-weight: 700; color: #F8FFFC; }
.hero-summary { display: block; margin-top: 16rpx; color: #B4D4C8; font-size: 23rpx; line-height: 1.5; }
.greet-score { flex-shrink: 0; width: 128rpx; height: 128rpx; border-radius: 50%; background: rgba(255, 255, 255, 0.1); border: 8rpx solid #F4C86A; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.greet-score-value { font-size: 44rpx; font-weight: 700; color: #F4C86A; line-height: 1; }
.greet-score-label { margin-top: 6rpx; font-size: 20rpx; color: #D7E9E2; }
.today-focus { display: flex; align-items: center; gap: 16rpx; margin-top: 20rpx; padding: 22rpx 24rpx; border-radius: 18rpx; background: #FFF9ED; border: 1rpx solid #F2E0B6; }.focus-icon { width: 44rpx; height: 44rpx; flex-shrink: 0; border-radius: 50%; background: #F7D783; color: #8A5E19; font-size: 28rpx; line-height: 44rpx; text-align: center; font-weight: 700; }.focus-copy { flex: 1; min-width: 0; }.focus-title { display: block; color: #493B20; font-size: 26rpx; font-weight: 700; }.focus-desc { display: block; margin-top: 6rpx; color: #8D7B54; font-size: 21rpx; line-height: 1.4; }.focus-arrow { color: #A36C1F; font-size: 36rpx; }
.overview-head { margin-top: 38rpx; }.section-kicker { display: block; color: #0E9F8E; font-size: 19rpx; letter-spacing: 2rpx; font-weight: 700; }.metric-strip { display: flex; margin-top: 18rpx; padding: 24rpx 8rpx; border-radius: 20rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 8rpx 20rpx rgba(31, 72, 55, 0.04); }.metric-item { flex: 1; min-width: 0; padding: 0 12rpx; border-right: 1rpx solid #E4ECE8; }.metric-item:last-child { border-right: none; }.metric-value { display: block; color: #173F35; font-size: 34rpx; font-weight: 700; white-space: nowrap; }.metric-unit { font-size: 21rpx; font-weight: 500; }.metric-label { display: block; margin-top: 8rpx; color: #50605A; font-size: 21rpx; white-space: nowrap; }.metric-status { display: block; margin-top: 6rpx; color: #9AA9A3; font-size: 19rpx; }.metric-status.good { color: #0E9F8E; }.quick-head { margin-top: 40rpx; }
.trend-card { margin-top: 32rpx; padding: 32rpx; border-radius: 24rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 12rpx 28rpx rgba(31, 72, 55, 0.06); }
.trend-chart { display: flex; justify-content: space-between; align-items: flex-end; height: 200rpx; margin-top: 24rpx; }
.trend-bar { display: flex; flex-direction: column; align-items: center; gap: 12rpx; }
.trend-track { width: 28rpx; height: 160rpx; border-radius: 999rpx; background: #E8F1ED; display: flex; align-items: flex-end; overflow: hidden; }
.trend-fill { width: 100%; border-radius: 999rpx; background: #0E9F8E; }
.trend-label { font-size: 22rpx; color: #71817A; }
.section-head { display: flex; justify-content: space-between; align-items: center; margin-top: 48rpx; }
.section-head.top-head { margin-top: 0; }
.section-head.compact { margin-top: 0; }
.section-title { display: block; font-size: 32rpx; font-weight: 700; color: #17231F; }
.section-link { font-size: 26rpx; color: #0E9F8E; font-weight: 600; }
.section-badge { padding: 8rpx 16rpx; border-radius: 999rpx; background: #E1F3ED; color: #0E9F8E; font-size: 22rpx; border: 1rpx solid #BFE3D6; }
.quick-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20rpx; margin-top: 24rpx; }
.quick-card { min-height: 160rpx; padding: 28rpx; border-radius: 20rpx; background: #FFFFFF; box-sizing: border-box; border: 1rpx solid #DDE7E1; box-shadow: 0 10rpx 24rpx rgba(31, 72, 55, 0.05); }
.quick-card.mint { background: #F0FAF6; border-color: #CBE9DD; }
.quick-card.blue { background: #F0F7FA; border-color: #C9E3E8; }
.quick-card.amber { background: #FFF7ED; border-color: #F3D8B7; }
.quick-icon-wrap { width: 56rpx; height: 56rpx; border-radius: 16rpx; display: flex; align-items: center; justify-content: center; background: #E1F3ED; }
.quick-icon { width: 32rpx; height: 32rpx; }
.quick-title { display: block; margin-top: 16rpx; font-size: 28rpx; line-height: 1.2; font-weight: 700; color: #17231F; }
.quick-desc { display: block; margin-top: 12rpx; font-size: 24rpx; line-height: 1.4; color: #71817A; }
</style>

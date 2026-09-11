<template>
  <view class="page-container">
    <view class="hero-panel">
      <view class="hero-main">
        <text class="date-text">2026年6月4日 · 智能健康管家</text>
        <text class="hero-title">早安，王先生</text>
        <text class="hero-desc">优先确认报告、药品库存和过敏史，AI 建议会更接近你的真实情况。</text>
        <view class="hero-actions">
          <button class="hero-btn primary" @click="goAdd">识别报告</button>
          <button class="hero-btn" @click="goChat">AI 解读</button>
        </view>
      </view>
      <view class="score-card">
        <text class="score-value">82</text>
        <text class="score-label">健康评分</text>
        <view class="score-line"><view class="score-fill"></view></view>
      </view>
    </view>

    <view class="summary-strip">
      <view class="summary-item">
        <text class="summary-value">{{ profilePercent }}%</text>
        <text class="summary-label">资料完整度</text>
      </view>
      <view class="summary-item">
        <text class="summary-value">2</text>
        <text class="summary-label">待确认资料</text>
      </view>
      <view class="summary-item warning">
        <text class="summary-value">3</text>
        <text class="summary-label">风险提醒</text>
      </view>
    </view>

    <view class="section-head">
      <text class="section-title">常用功能</text>
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

    <view class="priority-card">
      <view class="section-head compact">
        <text class="section-title">今天建议先做</text>
        <text class="section-badge">按优先级</text>
      </view>
      <view class="todo-item" v-for="(item, index) in todayActions" :key="item.title" @click="handleTodayAction(item)">
        <view class="todo-index" :class="item.theme">{{ index + 1 }}</view>
        <view class="todo-info">
          <text class="todo-title">{{ item.title }}</text>
          <text class="todo-desc">{{ item.desc }}</text>
        </view>
        <image class="arrow-icon" src="/static/icons/arrow-right.png" mode="aspectFit" />
      </view>
    </view>

    <view class="risk-panel">
      <view class="risk-head">
        <image class="risk-icon" src="/static/icons/warning.png" mode="aspectFit" />
        <view class="risk-copy">
          <text class="risk-title">健康风险摘要</text>
          <text class="risk-text">血压连续偏高，建议低盐饮食、规律监测，并在复诊时携带近 7 天血压记录。</text>
        </view>
      </view>
      <view class="risk-actions">
        <button class="mini-btn primary" @click="goRecord">查看趋势</button>
        <button class="mini-btn" @click="goChat">继续追问</button>
      </view>
    </view>

    <FloatingAction />
  </view>
</template>

<script>
import FloatingAction from '@/components/FloatingAction/FloatingAction.vue'
import { smoothNavigateTo, smoothSwitchTab } from '@/utils/router.js'

export default {
  components: { FloatingAction },
  data() {
    return {
      profilePercent: 72,
      quickActions: [
        { icon: '/static/icons/report.png', title: 'OCR 识别', desc: '体检/诊断/药盒', theme: 'mint', action: 'ocr' },
        { icon: '/static/icons/record.png', title: '健康趋势', desc: '指标变化与异常', theme: 'blue', action: 'record' },
        { icon: '/static/icons/pill.png', title: '药品管理', desc: '库存/有效期/提醒', theme: 'amber', action: 'medication' },
        { icon: '/static/icons/profile.png', title: '健康信息', desc: '病史与过敏史', theme: 'gray', action: 'profile' }
      ],
      todayActions: [
        { title: '确认体检报告识别结果', desc: '血压、血糖、血脂 12 项指标待确认', route: '/pages-sub/ocr_scan/ocr_scan', theme: 'blue' },
        { title: '补全阿司匹林库存', desc: '库存低于 20%，建议记录剩余数量', route: '/pages/medication/medication', theme: 'green' },
        { title: '完善过敏史与病史', desc: '用于 AI 判断用药禁忌和风险提醒', route: '/pages-sub/healthInfo/healthInfo', theme: 'amber' }
      ]
    }
  },
  methods: {
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
    handleTodayAction(item) {
      if (item.route === '/pages/medication/medication') {
        smoothSwitchTab(item.route)
        return
      }
      smoothNavigateTo(item.route)
    }
  }
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: linear-gradient(180deg, #EEFBF7 0%, #F8FAFC 34%, #F8FAFC 100%); padding: 28rpx 28rpx 170rpx; box-sizing: border-box; }
.hero-panel { display: flex; justify-content: space-between; align-items: stretch; gap: 20rpx; padding: 34rpx; border-radius: 18rpx; color: #fff; background: linear-gradient(135deg, #0F766E 0%, #10B981 52%, #2563EB 100%); box-shadow: 0 16rpx 36rpx rgba(13, 148, 136, 0.22); }
.hero-main { flex: 1; min-width: 0; }
.date-text { display: block; font-size: 23rpx; opacity: .84; }
.hero-title { display: block; margin-top: 12rpx; font-size: 44rpx; line-height: 1.12; font-weight: 900; }
.hero-desc { display: block; max-width: 470rpx; margin-top: 14rpx; font-size: 25rpx; line-height: 1.55; opacity: .9; }
.hero-actions { display: flex; gap: 14rpx; margin-top: 26rpx; }
.hero-btn { margin: 0; min-width: 140rpx; height: 66rpx; line-height: 66rpx; border-radius: 14rpx; background: rgba(255,255,255,.18); color: #fff; font-size: 25rpx; border: 1rpx solid rgba(255,255,255,.32); }
.hero-btn.primary { background: #FFFFFF; color: #0F766E; font-weight: 900; border-color: #FFFFFF; }
.score-card { width: 150rpx; padding: 20rpx 16rpx; border-radius: 16rpx; background: rgba(255,255,255,.16); display: flex; flex-direction: column; justify-content: center; border: 1rpx solid rgba(255,255,255,.24); flex-shrink: 0; box-sizing: border-box; }
.score-value { font-size: 50rpx; line-height: 1; font-weight: 900; }
.score-label { margin-top: 8rpx; font-size: 20rpx; opacity: .88; }
.score-line { height: 8rpx; margin-top: 16rpx; border-radius: 999rpx; background: rgba(255,255,255,.22); overflow: hidden; }
.score-fill { width: 82%; height: 100%; border-radius: 999rpx; background: #FFFFFF; }
.summary-strip { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14rpx; margin-top: 18rpx; }
.summary-item { padding: 20rpx 12rpx; border-radius: 16rpx; background: #FFFFFF; border: 1rpx solid #E8F0F2; text-align: center; box-shadow: 0 8rpx 22rpx rgba(15, 23, 42, .05); }
.summary-value { display: block; font-size: 34rpx; line-height: 1; color: #0F766E; font-weight: 900; }
.summary-item.warning .summary-value { color: #D97706; }
.summary-label { display: block; margin-top: 10rpx; font-size: 21rpx; color: #64748B; }
.section-head { display: flex; justify-content: space-between; align-items: center; margin-top: 30rpx; }
.section-head.compact { margin-top: 0; }
.section-title { display: block; font-size: 31rpx; font-weight: 900; color: #1E293B; }
.section-link { font-size: 24rpx; color: #0F766E; font-weight: 800; }
.section-badge { padding: 6rpx 14rpx; border-radius: 999rpx; background: #D1FAE5; color: #059669; font-size: 22rpx; }
.quick-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 18rpx; margin-top: 18rpx; }
.quick-card { min-height: 154rpx; padding: 22rpx; border-radius: 16rpx; background: #fff; box-shadow: 0 8rpx 22rpx rgba(15, 23, 42, .05); box-sizing: border-box; border: 1rpx solid #EEF2F7; }
.quick-card.mint { background: #F0FDF4; border-color: #BBF7D0; }
.quick-card.blue { background: #EFF6FF; border-color: #BFDBFE; }
.quick-card.amber { background: #FFFBEB; border-color: #FDE68A; }
.quick-icon-wrap { width: 54rpx; height: 54rpx; border-radius: 14rpx; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,.76); }
.quick-icon { width: 32rpx; height: 32rpx; }
.quick-title { display: block; margin-top: 12rpx; font-size: 28rpx; line-height: 1.2; font-weight: 900; color: #1E293B; }
.quick-desc { display: block; margin-top: 8rpx; font-size: 22rpx; line-height: 1.35; color: #64748B; }
.priority-card, .risk-panel { margin-top: 24rpx; padding: 28rpx; border-radius: 16rpx; background: #fff; box-shadow: 0 8rpx 22rpx rgba(15, 23, 42, .05); }
.todo-item { display: flex; align-items: center; gap: 18rpx; padding: 24rpx 0; border-bottom: 1rpx solid #F1F5F9; }
.todo-item:last-child { border-bottom: none; padding-bottom: 0; }
.todo-index { width: 52rpx; height: 52rpx; border-radius: 14rpx; display: flex; align-items: center; justify-content: center; color: #1E293B; font-size: 25rpx; font-weight: 900; flex-shrink: 0; }
.todo-index.blue { background: #DBEAFE; color: #1D4ED8; }
.todo-index.green { background: #D1FAE5; color: #047857; }
.todo-index.amber { background: #FEF3C7; color: #B45309; }
.todo-info { flex: 1; min-width: 0; }
.todo-title { display: block; font-size: 27rpx; color: #1E293B; font-weight: 900; line-height: 1.35; }
.todo-desc { display: block; margin-top: 8rpx; font-size: 23rpx; color: #64748B; line-height: 1.45; }
.arrow-icon { width: 24rpx; height: 24rpx; flex-shrink: 0; }
.risk-panel { background: linear-gradient(180deg, #FFFFFF, #FFF7ED); border: 1rpx solid #FED7AA; }
.risk-head { display: flex; gap: 18rpx; align-items: flex-start; }
.risk-icon { width: 44rpx; height: 44rpx; flex-shrink: 0; }
.risk-copy { flex: 1; min-width: 0; }
.risk-title { display: block; font-size: 30rpx; color: #9A3412; font-weight: 900; }
.risk-text { display: block; margin-top: 12rpx; font-size: 26rpx; line-height: 1.6; color: #9A3412; }
.risk-actions { display: flex; gap: 16rpx; margin-top: 24rpx; }
.mini-btn { flex: 1; height: 70rpx; line-height: 70rpx; border-radius: 14rpx; background: #FFFFFF; color: #334155; font-size: 26rpx; border: none; }
.mini-btn.primary { background: #0F766E; color: #fff; font-weight: 800; }
</style>

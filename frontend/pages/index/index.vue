<template>
  <view class="page-container">
    <view class="custom-nav">
      <view class="status-bar"></view>
      <view class="nav-content">
        <text class="nav-title">健康助手</text>
      </view>
    </view>
    
    <view class="page-content">
    <view class="greet-row">
      <view>
        <text class="greet-date">2026年6月4日 · 智能健康管家</text>
        <text class="greet-title">早安，王先生</text>
      </view>
      <view class="greet-score">
        <text class="greet-score-value">82</text>
        <text class="greet-score-label">健康评分</text>
      </view>
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
  </view>
</template>

<script>
import FloatingAction from '@/components/FloatingAction/FloatingAction.vue'
import { smoothNavigateTo, smoothSwitchTab } from '@/utils/router.js'

export default {
  components: { FloatingAction },
  data() {
    return {
      pressureTrend: [
        { day: '一', value: 62 }, { day: '二', value: 68 }, { day: '三', value: 74 },
        { day: '四', value: 71 }, { day: '五', value: 82 }, { day: '六', value: 78 }, { day: '日', value: 86 }
      ],
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
.page-container { min-height: 100vh; background: #F4F7F5; }
.custom-nav { position: fixed; top: 0; left: 0; right: 0; z-index: 999; background: rgba(244, 247, 245, 0.94); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-bottom: 1rpx solid #DDE7E1; }
.status-bar { height: var(--status-bar-height); }
.nav-content { height: 100rpx; padding: 0 32rpx; display: flex; align-items: center; justify-content: center; position: relative; }
.nav-title { position: absolute; left: 50%; transform: translateX(-50%); font-size: 36rpx; font-weight: 700; color: #17231F; }
.nav-actions { display: flex; gap: 20rpx; align-items: center; }
.nav-icon { width: 68rpx; height: 68rpx; border-radius: 50%; background: rgba(56, 189, 248, 0.12); display: flex; align-items: center; justify-content: center; font-size: 32rpx; border: 1rpx solid rgba(56, 189, 248, 0.2); }
.page-content { padding: 32rpx; padding-top: calc(var(--status-bar-height) + 100rpx + 24rpx); padding-bottom: 170rpx; }
.greet-row { display: flex; justify-content: space-between; align-items: center; }
.greet-date { display: block; font-size: 24rpx; color: #71817A; }
.greet-title { display: block; margin-top: 10rpx; font-size: 40rpx; font-weight: 700; color: #17231F; }
.greet-score { flex-shrink: 0; width: 128rpx; height: 128rpx; border-radius: 50%; background: #E1F3ED; border: 8rpx solid #0E9F8E; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.greet-score-value { font-size: 44rpx; font-weight: 700; color: #0E9F8E; line-height: 1; }
.greet-score-label { margin-top: 6rpx; font-size: 20rpx; color: #50605A; }
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
.priority-card { margin-top: 32rpx; padding: 32rpx; border-radius: 24rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 12rpx 28rpx rgba(31, 72, 55, 0.06); }
.todo-item { display: flex; align-items: center; gap: 20rpx; padding: 28rpx 0; border-bottom: 1rpx solid #E8F1ED; }
.todo-item:last-child { border-bottom: none; padding-bottom: 0; }
.todo-index { width: 56rpx; height: 56rpx; border-radius: 12rpx; display: flex; align-items: center; justify-content: center; color: #17231F; font-size: 26rpx; font-weight: 700; flex-shrink: 0; }
.todo-index.blue { background: #E8F3F6; color: #187A83; }
.todo-index.green { background: #E1F3ED; color: #0E9F8E; }
.todo-index.amber { background: rgba(249, 115, 22, 0.15); color: #F97316; }
.todo-info { flex: 1; min-width: 0; }
.todo-title { display: block; font-size: 28rpx; color: #17231F; font-weight: 600; line-height: 1.4; }
.todo-desc { display: block; margin-top: 10rpx; font-size: 24rpx; color: #71817A; line-height: 1.5; }
.arrow-icon { width: 24rpx; height: 24rpx; flex-shrink: 0; opacity: 0.5; }

.risk-panel { margin-top: 32rpx; padding: 32rpx; border-radius: 24rpx; background: #FFF7ED; border: 1rpx solid #F3D8B7; }
.risk-head { display: flex; gap: 20rpx; align-items: flex-start; }
.risk-icon { width: 48rpx; height: 48rpx; flex-shrink: 0; }
.risk-copy { flex: 1; min-width: 0; }
.risk-title { display: block; font-size: 30rpx; color: #B96B25; font-weight: 700; }
.risk-text { display: block; margin-top: 14rpx; font-size: 26rpx; line-height: 1.6; color: #70543B; }
.risk-actions { display: flex; gap: 16rpx; margin-top: 28rpx; }
.mini-btn { flex: 1; height: 72rpx; line-height: 72rpx; border-radius: 14rpx; background: #FFFFFF; color: #70543B; font-size: 26rpx; border: 1rpx solid #EBC99F; }
.mini-btn.primary { background: #E58A3A; color: #FFFFFF; font-weight: 700; border-color: #E58A3A; }
</style>

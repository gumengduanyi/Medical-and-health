<template>
  <view class="page-container">
    <view class="top-summary">
      <view>
        <text class="page-title">健康档案</text>
        <text class="page-desc">OCR 报告结构化后，自动生成指标趋势、风险提醒和复诊线索。</text>
      </view>
      <view class="score-pill">
        <text class="score-text">82</text>
        <text class="score-label">AI评分</text>
      </view>
    </view>

    <view class="tab-switch">
      <button class="tab-btn" :class="{ active: currentTab === 0 }" @click="switchTab(0)">指标趋势</button>
      <button class="tab-btn" :class="{ active: currentTab === 1 }" @click="switchTab(1)">报告库</button>
      <button class="tab-btn" :class="{ active: currentTab === 2 }" @click="switchTab(2)">诊疗记录</button>
    </view>

    <view class="insight-card">
      <text class="insight-title">AI 当前判断</text>
      <text class="insight-text">你的健康数据主要风险集中在血压和血糖趋势。建议优先确认最新体检报告，并连续记录 7 天血压。</text>
      <view class="insight-actions">
        <button class="insight-btn primary" @click="goOcrScan">上传报告</button>
        <button class="insight-btn" @click="goAiChat">AI 解读</button>
      </view>
    </view>

    <view v-if="currentTab === 0">
      <view class="metric-grid">
        <view class="metric-card warn"><text class="metric-label">血压</text><text class="metric-value">145/96</text><text class="metric-unit">mmHg · 偏高</text></view>
        <view class="metric-card"><text class="metric-label">空腹血糖</text><text class="metric-value">6.8</text><text class="metric-unit">mmol/L · 临界</text></view>
        <view class="metric-card"><text class="metric-label">BMI</text><text class="metric-value">22.9</text><text class="metric-unit">正常范围</text></view>
      </view>
      <view class="chart-card">
        <view class="section-head"><text class="section-title">近 7 天血压趋势</text><text class="section-tag">OCR+手动记录</text></view>
        <view class="bar-chart">
          <view class="bar-item" v-for="item in pressureList" :key="item.day">
            <view class="bar-track"><view class="bar-fill" :style="{ height: item.value + '%' }"></view></view>
            <text class="bar-label">{{ item.day }}</text>
          </view>
        </view>
      </view>
      <view class="ai-warning">
        <text class="warning-title">AI 异常指标预警</text>
        <text class="warning-text">血压连续偏高，建议低盐饮食、规律作息、每日固定时段监测。若伴随头晕胸闷，请及时就医。</text>
      </view>
    </view>

    <view v-if="currentTab === 1">
      <view class="report-card" v-for="item in reports" :key="item.title">
        <view class="report-icon-wrap"><image class="report-icon" src="/static/icons/report.png" mode="aspectFit" /></view>
        <view class="report-info"><text class="report-title">{{ item.title }}</text><text class="report-desc">{{ item.desc }}</text><text class="report-date">{{ item.date }}</text></view>
        <text class="report-status">{{ item.status }}</text>
      </view>
      <view class="empty-tip" @click="goOcrScan">上传报告后，系统会自动提取指标并关联到趋势图。点击去识别新报告。</view>
    </view>

    <view v-if="currentTab === 2">
      <view class="timeline-card" v-for="item in visits" :key="item.date">
        <view class="timeline-dot"></view>
        <view class="visit-body">
          <view class="visit-head"><text class="visit-date">{{ item.date }}</text><text class="visit-hospital">{{ item.hospital }}</text></view>
          <text class="visit-title">{{ item.title }}</text>
          <text class="visit-desc">{{ item.desc }}</text>
        </view>
      </view>
    </view>

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
      currentTab: 0,
      pressureList: [
        { day: '一', value: 62 }, { day: '二', value: 68 }, { day: '三', value: 74 }, { day: '四', value: 71 }, { day: '五', value: 82 }, { day: '六', value: 78 }, { day: '日', value: 86 }
      ],
      reports: [
        { title: '年度体检报告', desc: '已识别 36 项指标，3 项需关注', date: '2026-04-18', status: '已入库' },
        { title: '血常规化验单', desc: '白细胞、血红蛋白等指标正常', date: '2026-03-22', status: '已分析' },
        { title: '诊断证明', desc: '心内科复诊记录，已关联药品', date: '2026-03-22', status: '已关联' }
      ],
      visits: [
        { date: '2026-03-22', hospital: '市第一人民医院', title: '心内科 - 原发性高血压', desc: '主诉偶发性头晕，建议继续服用阿司匹林并增加运动。' },
        { date: '2026-01-05', hospital: '瑞金医院', title: '内分泌科 - 糖耐量异常', desc: '建议饮食控制并于三个月后复查空腹血糖。' }
      ]
    }
  },
  methods: {
    switchTab(index) { this.currentTab = index },
    goOcrScan() { smoothNavigateTo('/pages-sub/ocr_scan/ocr_scan') },
    goAiChat() { smoothNavigateTo('/pages-sub/ai_chat/ai_chat') }
  }
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: linear-gradient(180deg, #EEFBF7 0%, #F8FAFC 34%, #F8FAFC 100%); padding: 28rpx 28rpx 170rpx; box-sizing: border-box; }
.top-summary { display: flex; justify-content: space-between; align-items: center; padding: 34rpx; border-radius: 18rpx; background: linear-gradient(135deg, #0F766E, #10B981); color: #fff; box-shadow: 0 16rpx 36rpx rgba(13,148,136,.18); }
.page-title { display: block; font-size: 40rpx; font-weight: 900; }.page-desc { display: block; max-width: 480rpx; margin-top: 10rpx; font-size: 24rpx; line-height: 1.45; opacity: .88; }
.score-pill { width: 108rpx; height: 108rpx; border-radius: 16rpx; background: rgba(255,255,255,.18); display: flex; flex-direction: column; align-items: center; justify-content: center; flex-shrink: 0; }.score-text { font-size: 38rpx; font-weight: 900; }.score-label { font-size: 20rpx; opacity: .85; }
.tab-switch { display: flex; gap: 12rpx; margin: 24rpx 0; padding: 8rpx; border-radius: 16rpx; background: #E2E8F0; }.tab-btn { flex: 1; height: 66rpx; line-height: 66rpx; border-radius: 12rpx; background: transparent; color: #64748B; font-size: 25rpx; border: none; }.tab-btn.active { background: #FFFFFF; color: #0F766E; font-weight: 900; box-shadow: 0 6rpx 16rpx rgba(15,23,42,.06); }
.insight-card { margin-bottom: 24rpx; padding: 26rpx; border-radius: 16rpx; background: linear-gradient(135deg, #EFF6FF, #ECFDF5); border: 1rpx solid #BFDBFE; }
.insight-title { display: block; font-size: 29rpx; color: #0F766E; font-weight: 900; }.insight-text { display: block; margin-top: 10rpx; font-size: 25rpx; color: #334155; line-height: 1.55; }
.insight-actions { display: flex; gap: 16rpx; margin-top: 22rpx; }.insight-btn { flex: 1; height: 68rpx; line-height: 68rpx; border-radius: 14rpx; border: none; background: #fff; color: #334155; font-size: 25rpx; font-weight: 800; }.insight-btn.primary { background: #0F766E; color: #fff; }
.metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx; }.metric-card { padding: 24rpx 16rpx; border-radius: 16rpx; background: #fff; box-shadow: 0 8rpx 22rpx rgba(15,23,42,.05); border: 1rpx solid #EEF2F7; }.metric-card.warn { background: #FFF7ED; border-color: #FED7AA; }.metric-label { display: block; font-size: 22rpx; color: #64748B; }.metric-value { display: block; margin-top: 12rpx; font-size: 34rpx; font-weight: 900; color: #1E293B; }.metric-unit { display: block; margin-top: 8rpx; font-size: 20rpx; color: #94A3B8; }
.chart-card, .ai-warning, .report-card, .timeline-card { margin-top: 24rpx; padding: 30rpx; border: 1rpx solid #E8F0F2; border-radius: 16rpx; background: #fff; box-shadow: 0 8rpx 22rpx rgba(15,23,42,.05); }.section-head, .visit-head { display: flex; justify-content: space-between; align-items: center; }.section-title { font-size: 31rpx; color: #1E293B; font-weight: 900; }.section-tag { font-size: 22rpx; color: #0F766E; background: #ECFDF5; padding: 8rpx 14rpx; border-radius: 999rpx; }
.bar-chart { display: flex; justify-content: space-between; align-items: flex-end; height: 260rpx; margin-top: 26rpx; }.bar-item { display: flex; flex-direction: column; align-items: center; gap: 12rpx; }.bar-track { width: 34rpx; height: 210rpx; border-radius: 999rpx; background: #E2E8F0; display: flex; align-items: flex-end; overflow: hidden; }.bar-fill { width: 100%; border-radius: 999rpx; background: linear-gradient(180deg, #10B981, #2563EB); }.bar-label { font-size: 22rpx; color: #64748B; }
.ai-warning { background: #FFF7ED; border: 1rpx solid #FED7AA; }.warning-title { display: block; font-size: 30rpx; color: #9A3412; font-weight: 900; }.warning-text { display: block; margin-top: 14rpx; font-size: 26rpx; line-height: 1.6; color: #9A3412; }
.report-card { display: flex; align-items: center; gap: 20rpx; }.report-icon-wrap { width: 82rpx; height: 82rpx; border-radius: 16rpx; background: #ECFDF5; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }.report-icon { width: 44rpx; height: 44rpx; }.report-info { flex: 1; min-width: 0; }.report-title, .visit-title { display: block; font-size: 29rpx; font-weight: 900; color: #1E293B; }.report-desc, .visit-desc { display: block; margin-top: 8rpx; font-size: 24rpx; color: #64748B; line-height: 1.5; }.report-date, .visit-date { font-size: 22rpx; color: #94A3B8; }.report-status { color: #0F766E; font-size: 22rpx; }
.empty-tip { margin-top: 24rpx; padding: 24rpx; border-radius: 22rpx; background: #F8FAFC; color: #64748B; font-size: 24rpx; line-height: 1.5; text-align: center; }
.timeline-card { display: flex; gap: 20rpx; }.timeline-dot { width: 22rpx; height: 22rpx; margin-top: 10rpx; border-radius: 50%; background: #10B981; flex-shrink: 0; }.visit-body { flex: 1; }.visit-hospital { font-size: 22rpx; color: #94A3B8; }
</style>

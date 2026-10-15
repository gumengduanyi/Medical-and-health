<template>
  <view class="page-container">
    <view class="custom-nav">
      <view class="status-bar"></view>
      <view class="nav-content">
        <text class="nav-title">健康档案</text>
      </view>
    </view>

    <view class="page-content">
      <view class="score-banner">
        <view class="score-ring">
          <text class="score-value">82</text>
          <text class="score-unit">分</text>
        </view>
        <view class="score-info">
          <text class="score-title">AI 健康评分</text>
          <text class="score-desc">基于近期报告与日常记录综合评估</text>
        </view>
      </view>

      <view class="metric-row">
        <view class="metric-pill warn">
          <text class="metric-pill-label">血压</text>
          <text class="metric-pill-value">145/96</text>
          <text class="metric-pill-unit">mmHg · 偏高</text>
        </view>
        <view class="metric-pill">
          <text class="metric-pill-label">空腹血糖</text>
          <text class="metric-pill-value">6.8</text>
          <text class="metric-pill-unit">mmol/L · 临界</text>
        </view>
        <view class="metric-pill">
          <text class="metric-pill-label">BMI</text>
          <text class="metric-pill-value">22.9</text>
          <text class="metric-pill-unit">正常范围</text>
        </view>
      </view>

      <view class="record-entry" @click="goOcrScan">
        <view class="record-entry-icon"><image src="/static/icons/report.png" mode="aspectFit" /></view>
        <view class="record-entry-copy">
          <text class="record-entry-title">录入健康报告</text>
          <text class="record-entry-desc">识别体检报告、诊断记录和化验单</text>
        </view>
        <image class="record-entry-arrow" src="/static/icons/arrow-right.png" mode="aspectFit" />
      </view>

      <view class="tab-switch">
        <view class="tab-btn" :class="{ active: currentTab === 0 }" @click="switchTab(0)">指标趋势</view>
        <view class="tab-btn" :class="{ active: currentTab === 1 }" @click="switchTab(1)">报告库</view>
        <view class="tab-btn" :class="{ active: currentTab === 2 }" @click="switchTab(2)">诊疗记录</view>
      </view>

      <view v-if="currentTab === 0" class="tab-panel">
        <view class="chart-card">
          <view class="section-head">
            <text class="section-title">近 7 天血压趋势</text>
            <text class="section-tag">报告+手动记录</text>
          </view>
          <view class="bar-chart">
            <view class="bar-item" v-for="item in pressureList" :key="item.day">
              <view class="bar-track"><view class="bar-fill" :style="{ height: item.value + '%' }"></view></view>
              <text class="bar-label">{{ item.day }}</text>
            </view>
          </view>
        </view>
        <view class="ai-warning">
          <image class="warning-icon" src="/static/icons/warning.png" mode="aspectFit" />
          <view class="warning-body">
            <text class="warning-title">AI 异常指标预警</text>
            <text class="warning-text">血压连续偏高，建议低盐饮食、规律作息、每日固定时段监测。若伴随头晕胸闷，请及时就医。</text>
          </view>
        </view>
      </view>

      <view v-if="currentTab === 1" class="tab-panel">
        <view class="report-card" v-for="item in reports" :key="item.title">
          <view class="report-bar"></view>
          <view class="report-info">
            <view class="report-top">
              <text class="report-title">{{ item.title }}</text>
              <text class="report-status">{{ item.status }}</text>
            </view>
            <text class="report-desc">{{ item.desc }}</text>
            <text class="report-date">{{ item.date }}</text>
          </view>
        </view>
      </view>

      <view v-if="currentTab === 2" class="tab-panel">
        <view class="timeline">
          <view class="timeline-item" v-for="item in visits" :key="item.date">
            <view class="timeline-track">
              <view class="timeline-dot"></view>
              <view class="timeline-line"></view>
            </view>
            <view class="visit-body">
              <text class="visit-date">{{ item.date }}</text>
              <text class="visit-title">{{ item.title }}</text>
              <text class="visit-desc">{{ item.desc }}</text>
              <text class="visit-hospital">{{ item.hospital }}</text>
            </view>
          </view>
        </view>
      </view>

      <FloatingAction />
    </view>
  </view>
</template>

<script>
import FloatingAction from '@/components/FloatingAction/FloatingAction.vue'
import { smoothNavigateTo } from '@/utils/router.js'
import { getHealthRecords } from '@/services/modules/health.service.js'

export default {
  components: { FloatingAction },
  onShow() {
    this.loadReports()
  },
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
    async loadReports() {
      try {
        const records = await getHealthRecords()
        if (!Array.isArray(records)) return
        this.reports = records.map((item) => ({
          title: item.title || '健康报告',
          desc: Array.isArray(item.items) && item.items.length
            ? `已识别 ${item.items.length} 项指标${item.items.filter((field) => field.status === 'warning').length ? `，${item.items.filter((field) => field.status === 'warning').length} 项需关注` : ''}`
            : (item.content ? String(item.content).slice(0, 72) : '已保存的健康记录'),
          date: item.date || '未标注日期',
          status: item.status || '已入库'
        }))
      } catch (error) {
        uni.showToast({ title: error?.message || '报告加载失败', icon: 'none' })
      }
    },
    switchTab(index) { this.currentTab = index },
    goOcrScan() { smoothNavigateTo('/pages-sub/ocr_scan/ocr_scan') },
    goAiChat() { smoothNavigateTo('/pages-sub/ai_chat/ai_chat') }
  }
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: #F4F7F5; }
.custom-nav { position: fixed; top: 0; left: 0; right: 0; z-index: 999; background: rgba(244, 247, 245, 0.92); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-bottom: 1rpx solid #DDE7E1; }
.status-bar { height: var(--status-bar-height); }
.nav-content { height: 100rpx; padding: 0 32rpx; display: flex; align-items: center; justify-content: center; position: relative; }
.nav-title { position: absolute; left: 50%; transform: translateX(-50%); font-size: 36rpx; font-weight: 700; color: #17231F; }
.page-content { padding: 32rpx; padding-top: calc(var(--status-bar-height) + 100rpx + 32rpx); padding-bottom: 170rpx; }

.score-banner { display: flex; align-items: center; gap: 32rpx; padding: 40rpx; border-radius: 24rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 12rpx 28rpx rgba(31, 72, 55, 0.06); }
.score-ring { width: 136rpx; height: 136rpx; border-radius: 50%; background: conic-gradient(#0E9F8E 0deg, #0E9F8E 295deg, #DDE7E1 295deg); display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; flex-shrink: 0; }
.score-ring::before { content: ''; position: absolute; width: 104rpx; height: 104rpx; border-radius: 50%; background: #FFFFFF; }
.score-value { position: relative; z-index: 1; font-size: 52rpx; font-weight: 700; color: #17231F; line-height: 1; }
.score-unit { position: relative; z-index: 1; font-size: 24rpx; color: #71817A; margin-top: 4rpx; }
.score-info { flex: 1; }
.score-title { display: block; font-size: 36rpx; font-weight: 700; color: #17231F; }
.score-desc { display: block; margin-top: 12rpx; font-size: 26rpx; line-height: 1.5; color: #71817A; }

.metric-row { display: flex; gap: 16rpx; margin-top: 32rpx; }
.metric-pill { flex: 1; padding: 28rpx 20rpx; border-radius: 18rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; display: flex; flex-direction: column; align-items: center; }
.metric-pill.warn { background: #FFF7ED; border-color: #F3D8B7; }
.metric-pill-label { font-size: 24rpx; color: #71817A; }
.metric-pill-value { margin-top: 12rpx; font-size: 40rpx; font-weight: 700; color: #17231F; line-height: 1; }
.metric-pill-unit { margin-top: 10rpx; font-size: 22rpx; color: #9AA8A1; text-align: center; }

.record-entry { display: flex; align-items: center; gap: 20rpx; margin-top: 24rpx; padding: 24rpx; border-radius: 18rpx; background: #F0FAF6; border: 1rpx solid #BFE3D6; }
.record-entry-icon { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; border-radius: 16rpx; background: #E1F3ED; flex-shrink: 0; }.record-entry-icon image { width: 36rpx; height: 36rpx; }
.record-entry-copy { flex: 1; min-width: 0; }.record-entry-title { display: block; color: #17231F; font-size: 28rpx; font-weight: 700; }.record-entry-desc { display: block; margin-top: 8rpx; color: #71817A; font-size: 23rpx; line-height: 1.4; }.record-entry-arrow { width: 28rpx; height: 28rpx; opacity: 0.55; flex-shrink: 0; }

.tab-switch { display: flex; gap: 12rpx; margin-top: 40rpx; padding: 6rpx; border-radius: 16rpx; background: #E8F1ED; border: 1rpx solid #DDE7E1; }
.tab-btn { flex: 1; height: 72rpx; display: flex; align-items: center; justify-content: center; border-radius: 12rpx; background: transparent; color: #71817A; font-size: 28rpx; transition: all 0.2s; }
.tab-btn.active { background: #FFFFFF; color: #0E9F8E; font-weight: 700; box-shadow: 0 4rpx 12rpx rgba(31, 72, 55, 0.08); }

.tab-panel { animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10rpx); } to { opacity: 1; transform: translateY(0); } }

.chart-card { margin-top: 32rpx; padding: 36rpx; border-radius: 24rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 10rpx 24rpx rgba(31, 72, 55, 0.05); }
.section-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32rpx; }
.section-title { font-size: 32rpx; color: #17231F; font-weight: 700; }
.section-tag { font-size: 22rpx; color: #0E9F8E; background: #E1F3ED; padding: 8rpx 16rpx; border-radius: 999rpx; }

.bar-chart { display: flex; justify-content: space-between; align-items: flex-end; height: 300rpx; }
.bar-item { display: flex; flex-direction: column; align-items: center; gap: 16rpx; }
.bar-track { width: 40rpx; height: 240rpx; border-radius: 999rpx; background: #E8F1ED; display: flex; align-items: flex-end; overflow: hidden; }
.bar-fill { width: 100%; border-radius: 999rpx; background: #0E9F8E; transition: height 0.4s ease; }
.bar-label { font-size: 24rpx; color: #71817A; }

.ai-warning { margin-top: 32rpx; padding: 32rpx; border-radius: 20rpx; background: rgba(249, 115, 22, 0.08); border: 1rpx solid rgba(249, 115, 22, 0.2); display: flex; gap: 20rpx; align-items: flex-start; }
.warning-icon { width: 48rpx; height: 48rpx; flex-shrink: 0; }
.warning-body { flex: 1; }
.warning-title { display: block; font-size: 30rpx; color: #F97316; font-weight: 700; }
.warning-text { display: block; margin-top: 12rpx; font-size: 26rpx; line-height: 1.65; color: #CBD5E1; }

.report-card { margin-top: 20rpx; padding: 28rpx 32rpx; border-radius: 18rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; display: flex; gap: 20rpx; overflow: hidden; box-shadow: 0 8rpx 20rpx rgba(31, 72, 55, 0.04); }
.report-card:first-child { margin-top: 32rpx; }
.report-bar { width: 6rpx; border-radius: 999rpx; background: #0E9F8E; flex-shrink: 0; }
.report-info { flex: 1; min-width: 0; }
.report-top { display: flex; justify-content: space-between; align-items: center; gap: 16rpx; }
.report-title { font-size: 30rpx; font-weight: 700; color: #17231F; }
.report-status { font-size: 24rpx; color: #0E9F8E; font-weight: 600; flex-shrink: 0; }
.report-desc { display: block; margin-top: 10rpx; font-size: 26rpx; color: #71817A; line-height: 1.5; }
.report-date { display: block; margin-top: 10rpx; font-size: 24rpx; color: #9AA8A1; }

.timeline { margin-top: 32rpx; }
.timeline-item { display: flex; gap: 24rpx; }
.timeline-track { display: flex; flex-direction: column; align-items: center; width: 28rpx; flex-shrink: 0; }
.timeline-dot { width: 24rpx; height: 24rpx; border-radius: 50%; background: #0E9F8E; flex-shrink: 0; box-shadow: 0 0 0 6rpx rgba(14, 159, 142, 0.15); }
.timeline-line { flex: 1; width: 2rpx; background: #DDE7E1; margin: 8rpx 0; }
.timeline-item:last-child .timeline-line { display: none; }
.visit-body { flex: 1; padding-bottom: 40rpx; }
.visit-date { display: block; font-size: 24rpx; color: #9AA8A1; font-weight: 600; }
.visit-title { display: block; margin-top: 10rpx; font-size: 30rpx; font-weight: 700; color: #17231F; }
.visit-desc { display: block; margin-top: 10rpx; font-size: 26rpx; color: #71817A; line-height: 1.65; }
.visit-hospital { display: block; margin-top: 10rpx; font-size: 24rpx; color: #9AA8A1; }
</style>

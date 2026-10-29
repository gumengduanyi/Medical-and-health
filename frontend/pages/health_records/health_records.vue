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

      <view class="section-head trend-head">
        <text class="section-title">近 7 天血压趋势</text>
        <text class="section-tag">报告+手动记录</text>
      </view>
      <view class="chart-card">
        <view class="bar-chart">
          <view class="bar-item" v-for="item in pressureList" :key="item.day">
            <view class="bar-track"><view class="bar-fill" :style="{ height: item.value + '%' }"></view></view>
            <text class="bar-label">{{ item.day }}</text>
          </view>
        </view>
      </view>

      <view class="archive-links">
        <view class="archive-link" @click="goReportLibrary">
          <view class="archive-link-icon report-icon"><image src="/static/icons/report.png" mode="aspectFit" /></view>
          <view class="archive-link-copy">
            <text class="archive-link-title">报告库</text>
            <text class="archive-link-desc">查看体检、化验和诊断资料</text>
          </view>
          <image class="archive-link-arrow" src="/static/icons/arrow-right.png" mode="aspectFit" />
        </view>
        <view class="archive-link" @click="goVisitRecords">
          <view class="archive-link-icon visit-icon"><image src="/static/icons/record.png" mode="aspectFit" /></view>
          <view class="archive-link-copy">
            <text class="archive-link-title">诊疗记录</text>
            <text class="archive-link-desc">查看就诊时间线和医生建议</text>
          </view>
          <image class="archive-link-arrow" src="/static/icons/arrow-right.png" mode="aspectFit" />
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
      pressureList: [
        { day: '一', value: 62 }, { day: '二', value: 68 }, { day: '三', value: 74 }, { day: '四', value: 71 }, { day: '五', value: 82 }, { day: '六', value: 78 }, { day: '日', value: 86 }
      ],
    }
  },
  methods: {
    goOcrScan() { smoothNavigateTo('/pages-sub/ocr_scan/ocr_scan') },
    goAiChat() { smoothNavigateTo('/pages-sub/ai_chat/ai_chat') },
    goReportLibrary() { smoothNavigateTo('/pages/report_library/report_library') },
    goVisitRecords() { smoothNavigateTo('/pages/visit_records/visit_records') }
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

.section-head { display: flex; justify-content: space-between; align-items: center; }
.trend-head { margin-top: 40rpx; }
.section-title { font-size: 32rpx; color: #17231F; font-weight: 700; }
.section-tag { font-size: 22rpx; color: #0E9F8E; background: #E1F3ED; padding: 8rpx 16rpx; border-radius: 999rpx; }

.chart-card { margin-top: 20rpx; padding: 36rpx; border-radius: 24rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 10rpx 24rpx rgba(31, 72, 55, 0.05); }

.bar-chart { display: flex; justify-content: space-between; align-items: flex-end; height: 300rpx; }
.bar-item { display: flex; flex-direction: column; align-items: center; gap: 16rpx; }
.bar-track { width: 40rpx; height: 240rpx; border-radius: 999rpx; background: #E8F1ED; display: flex; align-items: flex-end; overflow: hidden; }
.bar-fill { width: 100%; border-radius: 999rpx; background: #0E9F8E; transition: height 0.4s ease; }
.bar-label { font-size: 24rpx; color: #71817A; }

.archive-links { margin-top: 28rpx; }
.archive-link { display: flex; align-items: center; gap: 20rpx; margin-top: 16rpx; padding: 24rpx; border-radius: 18rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 8rpx 20rpx rgba(31, 72, 55, 0.04); }
.archive-link:first-child { margin-top: 0; }
.archive-link-icon { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; border-radius: 16rpx; flex-shrink: 0; }
.archive-link-icon image { width: 36rpx; height: 36rpx; }
.report-icon { background: #E1F3ED; }
.visit-icon { background: #E8F3F6; }
.archive-link-copy { flex: 1; min-width: 0; }
.archive-link-title { display: block; font-size: 30rpx; font-weight: 700; color: #17231F; }
.archive-link-desc { display: block; margin-top: 8rpx; font-size: 24rpx; line-height: 1.4; color: #71817A; }
.archive-link-arrow { width: 28rpx; height: 28rpx; opacity: 0.55; flex-shrink: 0; }
</style>

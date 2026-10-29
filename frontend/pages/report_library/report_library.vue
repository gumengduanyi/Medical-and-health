<template>
  <view class="page-container">
    <view class="custom-nav">
      <view class="status-bar"></view>
      <view class="nav-content">
        <view class="nav-back" @click="goBack"><text class="nav-back-icon">‹</text></view>
        <text class="nav-title">报告库</text>
      </view>
    </view>

    <view class="page-content">
      <view v-if="trendResult" class="report-card">
        <text>已确认报告的指标趋势</text>
        <view v-for="trend in trendResult.trends" :key="trend.label + trend.unit">
          <text>{{ trend.label }}（{{ trend.unit }}）</text>
          <view v-for="point in trend.points" :key="point.record_id + point.date">{{ point.date }}：{{ point.value }}；参考 {{ point.reference || '未标注' }}</view>
          <view>变化量：{{ trend.delta === null ? '数据不足或同日结果待核对' : trend.delta }}</view>
          <view v-if="trend.reference_changed">参考范围发生变化，请核对</view>
        </view>
        <view v-for="(item, index) in trendResult.excluded" :key="index">{{ item.label || item.record_id }}：{{ item.reason }}</view>
        <text>{{ trendResult.notice }}</text>
      </view>
      <view class="page-intro">
        <view>
          <text class="page-title">健康报告</text>
          <text class="page-subtitle">集中查看已保存的体检、化验和诊断资料</text>
        </view>
        <text class="report-count">{{ reports.length }} 份</text>
      </view>

      <view class="record-entry" @click="goOcrScan">
        <view class="record-entry-icon"><image src="/static/icons/report.png" mode="aspectFit" /></view>
        <view class="record-entry-copy">
          <text class="record-entry-title">录入健康报告</text>
          <text class="record-entry-desc">识别体检报告、诊断记录和化验单</text>
        </view>
        <image class="record-entry-arrow" src="/static/icons/arrow-right.png" mode="aspectFit" />
      </view>

      <view class="filter-block">
        <text class="filter-label">时间范围</text>
        <view class="filter-row">
          <view
            v-for="option in timeOptions"
            :key="option.value"
            class="filter-option"
            :class="{ active: timeFilter === option.value }"
            @click="timeFilter = option.value"
          >{{ option.label }}</view>
        </view>
      </view>

      <view v-if="filteredReports.length" class="report-list">
        <view class="report-card" v-for="item in filteredReports" :key="item.id || item.title">
          <view class="report-bar"></view>
          <view class="report-info">
            <view class="report-top">
              <text class="report-title">{{ item.title }}</text>
              <text class="report-status">{{ item.status }}</text>
            </view>
            <text class="report-desc">{{ item.desc }}</text>
            <text class="report-date">{{ item.date }}</text>
          </view>
          <image class="report-arrow" src="/static/icons/arrow-right.png" mode="aspectFit" />
        </view>
      </view>
      <view v-else class="empty-state">
        <text class="empty-title">这个时间范围内没有报告</text>
        <text class="empty-desc">可以切换时间范围，或录入一份新的健康报告</text>
      </view>

      <FloatingAction />
    </view>
  </view>
</template>

<script>
import FloatingAction from '@/components/FloatingAction/FloatingAction.vue'
import { smoothNavigateTo } from '@/utils/router.js'
import { analyzeTrends } from '@/services/modules/workflow.service.js'
import { getHealthRecords } from '@/services/modules/health.service.js'

export default {
  components: { FloatingAction },
  data() {
    return {
      trendResult: null,
      reports: [
        { id: 'annual-checkup', title: '年度体检报告', desc: '已识别 36 项指标，3 项需关注', date: '2026-04-18', status: '已入库' },
        { id: 'blood-test', title: '血常规化验单', desc: '白细胞、血红蛋白等指标正常', date: '2026-03-22', status: '已分析' },
        { id: 'diagnosis', title: '诊断证明', desc: '心内科复诊记录，已关联药品', date: '2026-03-22', status: '已关联' }
      ],
      timeFilter: 'all',
      timeOptions: [
        { label: '全部', value: 'all' },
        { label: '近3个月', value: '3m' },
        { label: '近6个月', value: '6m' },
        { label: '今年', value: 'year' }
      ]
    }
  },
  computed: {
    filteredReports() {
      return this.reports.filter((item) => this.isWithinTimeRange(item.date))
    }
  },
  onShow() {
    this.loadReports()
  },
  methods: {
    goBack() {
      uni.navigateBack()
    },
    async loadReports() {
      try {
        const records = await getHealthRecords()
        if (!Array.isArray(records)) return
        this.trendResult = await analyzeTrends(records)
        this.reports = records.map((item, index) => ({
          id: item.id || `report-${index}`,
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
    goOcrScan() {
      smoothNavigateTo('/pages-sub/ocr_scan/ocr_scan')
    },
    isWithinTimeRange(dateText) {
      if (this.timeFilter === 'all' || !/^\d{4}-\d{2}-\d{2}$/.test(dateText)) return true
      const date = new Date(`${dateText}T00:00:00`)
      const now = new Date()
      if (this.timeFilter === 'year') return date.getFullYear() === now.getFullYear()
      const months = this.timeFilter === '3m' ? 3 : 6
      const start = new Date(now.getFullYear(), now.getMonth() - months, now.getDate())
      return date >= start && date <= now
    }
  }
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: #F4F7F5; }
.custom-nav { position: fixed; top: 0; left: 0; right: 0; z-index: 999; background: rgba(244, 247, 245, 0.92); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-bottom: 1rpx solid #DDE7E1; }
.status-bar { height: var(--status-bar-height); }
.nav-content { height: 100rpx; padding: 0 32rpx; display: flex; align-items: center; justify-content: center; position: relative; }
.nav-back { position: absolute; left: 32rpx; width: 60rpx; height: 60rpx; display: flex; align-items: center; justify-content: center; }
.nav-back-icon { font-size: 56rpx; color: #17231F; font-weight: 300; line-height: 1; }
.nav-title { position: absolute; left: 50%; transform: translateX(-50%); font-size: 36rpx; font-weight: 700; color: #17231F; }
.page-content { padding: 32rpx; padding-top: calc(var(--status-bar-height) + 100rpx + 32rpx); padding-bottom: 170rpx; }
.page-intro { display: flex; align-items: flex-end; justify-content: space-between; gap: 20rpx; }
.page-title { display: block; font-size: 40rpx; font-weight: 700; color: #17231F; }
.page-subtitle { display: block; margin-top: 10rpx; font-size: 24rpx; line-height: 1.5; color: #71817A; }
.report-count { flex-shrink: 0; color: #0E9F8E; font-size: 26rpx; font-weight: 700; }
.record-entry { display: flex; align-items: center; gap: 20rpx; margin-top: 28rpx; padding: 24rpx; border-radius: 18rpx; background: #F0FAF6; border: 1rpx solid #BFE3D6; }
.record-entry-icon { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; border-radius: 16rpx; background: #E1F3ED; flex-shrink: 0; }
.record-entry-icon image { width: 36rpx; height: 36rpx; }
.record-entry-copy { flex: 1; min-width: 0; }
.record-entry-title { display: block; color: #17231F; font-size: 28rpx; font-weight: 700; }
.record-entry-desc { display: block; margin-top: 8rpx; color: #71817A; font-size: 23rpx; line-height: 1.4; }
.record-entry-arrow, .report-arrow { width: 28rpx; height: 28rpx; opacity: 0.55; flex-shrink: 0; }
.filter-block { margin-top: 30rpx; }
.filter-label { display: block; font-size: 24rpx; color: #71817A; }
.filter-row { display: flex; gap: 12rpx; margin-top: 14rpx; }
.filter-option { flex: 1; height: 64rpx; display: flex; align-items: center; justify-content: center; border-radius: 12rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; color: #71817A; font-size: 23rpx; }
.filter-option.active { background: #E1F3ED; border-color: #BFE3D6; color: #0E9F8E; font-weight: 700; }
.report-list { margin-top: 28rpx; }
.report-card { display: flex; align-items: center; gap: 20rpx; margin-top: 20rpx; padding: 28rpx 24rpx 28rpx 32rpx; border-radius: 18rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 8rpx 20rpx rgba(31, 72, 55, 0.04); }
.report-card:first-child { margin-top: 0; }
.report-bar { width: 6rpx; align-self: stretch; border-radius: 999rpx; background: #0E9F8E; flex-shrink: 0; }
.report-info { flex: 1; min-width: 0; }
.report-top { display: flex; justify-content: space-between; align-items: center; gap: 16rpx; }
.report-title { font-size: 30rpx; font-weight: 700; color: #17231F; }
.report-status { font-size: 24rpx; color: #0E9F8E; font-weight: 600; flex-shrink: 0; }
.report-desc { display: block; margin-top: 10rpx; font-size: 26rpx; color: #71817A; line-height: 1.5; }
.report-date { display: block; margin-top: 10rpx; font-size: 24rpx; color: #9AA8A1; }
.empty-state { margin-top: 28rpx; padding: 64rpx 32rpx; border-radius: 20rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; text-align: center; }
.empty-title { display: block; font-size: 30rpx; font-weight: 700; color: #17231F; }
.empty-desc { display: block; margin-top: 12rpx; color: #71817A; font-size: 24rpx; line-height: 1.5; }
</style>

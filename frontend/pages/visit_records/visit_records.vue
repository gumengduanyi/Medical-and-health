<template>
  <view class="page-container">
    <view class="custom-nav">
      <view class="status-bar"></view>
      <view class="nav-content">
        <view class="nav-back" @click="goBack"><text class="nav-back-icon">‹</text></view>
        <text class="nav-title">诊疗记录</text>
      </view>
    </view>

    <view class="page-content">
      <view class="page-intro">
        <view>
          <text class="page-title">就诊时间线</text>
          <text class="page-subtitle">记录每次就诊、诊断和医生建议</text>
        </view>
        <text class="record-count">{{ visits.length }} 次</text>
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

      <view v-if="filteredVisits.length" class="timeline">
        <view class="timeline-item" v-for="(item, index) in filteredVisits" :key="item.id || item.date">
          <view class="timeline-track">
            <view class="timeline-dot"></view>
            <view v-if="index < filteredVisits.length - 1" class="timeline-line"></view>
          </view>
          <view class="visit-card">
            <text class="visit-date">{{ item.date }}</text>
            <text class="visit-title">{{ item.title }}</text>
            <text class="visit-desc">{{ item.desc }}</text>
            <text class="visit-hospital">{{ item.hospital }}</text>
          </view>
        </view>
      </view>
      <view v-else class="empty-state">
        <text class="empty-title">这个时间范围内没有诊疗记录</text>
        <text class="empty-desc">可以切换时间范围，或保存新的就诊信息</text>
      </view>

      <FloatingAction />
    </view>
  </view>
</template>

<script>
import FloatingAction from '@/components/FloatingAction/FloatingAction.vue'

export default {
  components: { FloatingAction },
  data() {
    return {
      visits: [
        { id: 'visit-2026-03-22', date: '2026-03-22', hospital: '市第一人民医院', title: '心内科 - 原发性高血压', desc: '主诉偶发性头晕，建议继续服用阿司匹林并增加运动。' },
        { id: 'visit-2026-01-05', date: '2026-01-05', hospital: '瑞金医院', title: '内分泌科 - 糖耐量异常', desc: '建议饮食控制并于三个月后复查空腹血糖。' }
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
    filteredVisits() {
      return this.visits.filter((item) => this.isWithinTimeRange(item.date))
    }
  },
  methods: {
    isWithinTimeRange(dateText) {
      if (this.timeFilter === 'all' || !/^\d{4}-\d{2}-\d{2}$/.test(dateText)) return true
      const date = new Date(`${dateText}T00:00:00`)
      const now = new Date()
      if (this.timeFilter === 'year') return date.getFullYear() === now.getFullYear()
      const months = this.timeFilter === '3m' ? 3 : 6
      const start = new Date(now.getFullYear(), now.getMonth() - months, now.getDate())
      return date >= start && date <= now
    }
  },
  methods: {
    goBack() {
      uni.navigateBack()
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
.record-count { flex-shrink: 0; color: #0E9F8E; font-size: 26rpx; font-weight: 700; }
.filter-block { margin-top: 30rpx; }
.filter-label { display: block; font-size: 24rpx; color: #71817A; }
.filter-row { display: flex; gap: 12rpx; margin-top: 14rpx; }
.filter-option { flex: 1; height: 64rpx; display: flex; align-items: center; justify-content: center; border-radius: 12rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; color: #71817A; font-size: 23rpx; }
.filter-option.active { background: #E8F3F6; border-color: #C9E3E8; color: #187A83; font-weight: 700; }
.timeline { margin-top: 36rpx; }
.timeline-item { display: flex; gap: 24rpx; min-height: 190rpx; }
.timeline-track { display: flex; flex-direction: column; align-items: center; width: 28rpx; flex-shrink: 0; }
.timeline-dot { width: 24rpx; height: 24rpx; border-radius: 50%; background: #0E9F8E; flex-shrink: 0; box-shadow: 0 0 0 6rpx rgba(14, 159, 142, 0.15); }
.timeline-line { flex: 1; width: 2rpx; background: #DDE7E1; margin: 8rpx 0; }
.visit-card { flex: 1; margin-bottom: 24rpx; padding: 28rpx; border-radius: 18rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 8rpx 20rpx rgba(31, 72, 55, 0.04); }
.visit-date { display: block; font-size: 24rpx; color: #9AA8A1; font-weight: 600; }
.visit-title { display: block; margin-top: 10rpx; font-size: 30rpx; font-weight: 700; color: #17231F; }
.visit-desc { display: block; margin-top: 10rpx; font-size: 26rpx; color: #71817A; line-height: 1.65; }
.visit-hospital { display: block; margin-top: 10rpx; font-size: 24rpx; color: #9AA8A1; }
.empty-state { margin-top: 28rpx; padding: 64rpx 32rpx; border-radius: 20rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; text-align: center; }
.empty-title { display: block; font-size: 30rpx; font-weight: 700; color: #17231F; }
.empty-desc { display: block; margin-top: 12rpx; color: #71817A; font-size: 24rpx; line-height: 1.5; }
</style>

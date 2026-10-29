<template>
  <view class="page-container">
    <view class="custom-nav">
      <view class="status-bar"></view>
      <view class="nav-content">
        <text class="nav-title">档案管理</text>
        <image class="nav-cat" :src="catImageUrl" mode="aspectFit" />
      </view>
    </view>

    <view class="page-content">
      <view class="record-entry" @click="goOcrScan">
        <view class="record-entry-icon"><image src="/static/icons/report.png" mode="aspectFit" /></view>
        <view class="record-entry-copy">
          <text class="record-entry-title">档案智能录入</text>
          <text class="record-entry-desc">拍摄或上传报告，识别后自动归档</text>
        </view>
        <image class="record-entry-arrow" src="/static/icons/arrow-right.png" mode="aspectFit" />
      </view>

      <text class="sub-title">档案分类</text>
      <view class="category-grid">
        <view class="category-card" v-for="item in categories" :key="item.name" @click="goCategory(item.name)">
          <text class="category-emoji">{{ item.emoji }}</text>
          <text class="category-name">{{ item.name }}</text>
          <text class="category-count">{{ item.count }} 份</text>
        </view>
      </view>

      <text class="sub-title">诊疗记录</text>
      <view class="timeline">
        <view class="timeline-item" v-for="item in visits" :key="item.date + item.title">
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
  </view>
</template>

<script>
import { smoothNavigateTo } from '@/utils/router.js'
import { getReports } from '@/services/modules/health.service.js'

export default {
  onShow() {
    this.loadReportCounts()
  },
  data() {
    return {
      catImageUrl: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20cartoon%20kitten%20sticker%2C%20flat%20vector%20illustration%2C%20big%20round%20eyes%2C%20rosy%20cheeks%2C%20mint%20green%20scarf%2C%20kawaii%20style%2C%20clean%20transparent-like%20background&image_size=square',
      categories: [
        { name: '体检报告', emoji: '🩺', count: 0 },
        { name: '门诊报告', emoji: '🏥', count: 0 },
        { name: '住院报告', emoji: '🛏️', count: 0 },
        { name: '急诊报告', emoji: '🚑', count: 0 },
        { name: '其他报告', emoji: '📁', count: 0 }
      ],
      visits: [
        { date: '2026-03-22', hospital: '市第一人民医院', title: '心内科 - 原发性高血压', desc: '主诉偶发性头晕，建议继续服用阿司匹林并增加运动。' },
        { date: '2026-01-05', hospital: '瑞金医院', title: '内分泌科 - 糖耐量异常', desc: '建议饮食控制并于三个月后复查空腹血糖。' }
      ]
    }
  },
  methods: {
    async loadReportCounts() {
      try {
        const reports = await getReports()
        if (!Array.isArray(reports)) return
        this.categories = this.categories.map((item) => ({
          ...item,
          count: reports.filter((report) => report.category === item.name).length
        }))
      } catch (error) {
        // 统计失败时保留 0，不影响页面其他内容
      }
    },
    goOcrScan() { smoothNavigateTo('/pages-sub/ocr_scan/ocr_scan') },
    goCategory(category) {
      smoothNavigateTo(`/pages-sub/report_category/report_category?category=${encodeURIComponent(category)}`)
    }
  }
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: #F4F7F5; }
.custom-nav { position: fixed; top: 0; left: 0; right: 0; z-index: 999; background: rgba(244, 247, 245, 0.92); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-bottom: 1rpx solid #DDE7E1; }
.status-bar { height: var(--status-bar-height); }
.nav-content { height: 112rpx; padding: 0 32rpx; display: flex; align-items: center; justify-content: space-between; }
.nav-title { font-size: 48rpx; font-weight: 700; color: #17231F; letter-spacing: 2rpx; }
.nav-cat { width: 92rpx; height: 92rpx; animation: cat-bounce 2.6s ease-in-out infinite; }
@keyframes cat-bounce { 0%, 100% { transform: translateY(0) rotate(-6deg); } 50% { transform: translateY(-8rpx) rotate(6deg); } }
.page-content { padding: 32rpx; padding-top: calc(var(--status-bar-height) + 112rpx + 32rpx); padding-bottom: 120rpx; }

.record-entry { display: flex; align-items: center; gap: 20rpx; padding: 28rpx; border-radius: 20rpx; background: #F0FAF6; border: 1rpx solid #BFE3D6; }
.record-entry-icon { width: 72rpx; height: 72rpx; display: flex; align-items: center; justify-content: center; border-radius: 16rpx; background: #E1F3ED; flex-shrink: 0; }
.record-entry-icon image { width: 40rpx; height: 40rpx; }
.record-entry-copy { flex: 1; min-width: 0; }
.record-entry-title { display: block; color: #17231F; font-size: 30rpx; font-weight: 700; }
.record-entry-desc { display: block; margin-top: 8rpx; color: #71817A; font-size: 24rpx; line-height: 1.4; }
.record-entry-arrow { width: 28rpx; height: 28rpx; opacity: 0.55; flex-shrink: 0; }

.sub-title { display: block; margin: 40rpx 0 20rpx; color: #17231F; font-size: 32rpx; font-weight: 700; }

.category-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20rpx; }
.category-card { display: flex; flex-direction: column; align-items: center; padding: 28rpx 12rpx; border-radius: 20rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 8rpx 20rpx rgba(31, 72, 55, 0.04); }
.category-emoji { font-size: 44rpx; line-height: 1; }
.category-name { margin-top: 14rpx; color: #17231F; font-size: 26rpx; font-weight: 700; }
.category-count { margin-top: 8rpx; color: #9AA8A1; font-size: 22rpx; }

.timeline { margin-top: 8rpx; }
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

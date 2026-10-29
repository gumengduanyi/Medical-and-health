<template>
  <view class="page-container">
    <view class="custom-nav">
      <view class="status-bar"></view>
      <view class="nav-content">
        <text class="nav-title">智慧药箱</text>
      </view>
    </view>
    
    <view class="page-content">
    <view v-if="cabinetFindings.length" class="medicine-card">
      <text>药箱核查（库存阈值 3，临期 30 天）</text>
      <view v-for="(finding, index) in cabinetFindings" :key="index">{{ finding.name }}：{{ finding.message }}</view>
    </view>
    <view class="search-box">
      <text class="search-icon">🔍</text>
      <input class="search-input" placeholder="搜索药品、功效、说明书、禁忌" />
    </view>

    <view class="med-entry-grid">
      <view class="entry-card primary" @click="goAdd">
        <image class="entry-icon" src="/static/icons/plus.png" mode="aspectFit" />
        <text class="entry-title">手动录入药品</text>
        <text class="entry-desc">名称、剂量、库存</text>
      </view>
      <view class="entry-card" @click="goOcrScan">
        <image class="entry-icon" src="/static/icons/report.png" mode="aspectFit" />
        <text class="entry-title">药箱智能录入</text>
        <text class="entry-desc">识别药盒/说明书</text>
      </view>
      <view class="entry-card" @click="goAiChat">
        <image class="entry-icon" src="/static/icons/sparkle.png" mode="aspectFit" />
        <text class="entry-title">问 AI 用药</text>
        <text class="entry-desc">禁忌与相互作用</text>
      </view>
    </view>

    <view class="section-card adherence-card">
      <view class="section-head">
        <text class="section-title">本周服药执行率</text>
        <text class="rate-value">96%</text>
      </view>
      <view class="week-row">
        <view class="day-item" v-for="(item, index) in weekList" :key="index">
          <view class="day-circle" :class="{ done: item.done, today: item.isToday }">{{ item.label }}</view>
          <text class="day-mark">{{ item.done ? '✓' : '○' }}</text>
        </view>
      </view>
    </view>

    <view class="section-head list-head">
      <text class="section-title">药品库存</text>
      <text class="section-subtitle">AI 已识别 8 种药品</text>
    </view>

    <view class="medicine-card" v-for="item in medicines" :key="item.name">
      <view class="med-icon-bg" :class="item.theme">
        <image class="med-icon" src="/static/icons/pill.png" mode="aspectFit" />
      </view>
      <view class="med-body">
        <view class="med-title-row">
          <text class="med-name">{{ item.name }}</text>
          <text class="stock-tag" :class="item.level">{{ item.stock }}</text>
        </view>
        <text class="med-desc">{{ item.dose }}</text>
        <text class="expire-date">有效期至：{{ item.expire }}</text>
        <view class="progress-bar"><view class="progress-fill" :class="item.level" :style="{ width: item.percent + '%' }"></view></view>
        <view class="risk-row" v-if="item.risk">
          <text class="risk-dot">!</text>
          <text class="risk-text">{{ item.risk }}</text>
        </view>
        <view class="med-actions">
          <button class="med-action primary" @click="goAdd">补充记录</button>
          <button class="med-action" @click="showMedTip(item)">查看建议</button>
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
import { inspectCabinet } from '@/services/modules/workflow.service.js'
import { getMedicines } from '@/services/modules/medicine.service.js'

export default {
  components: { FloatingAction },
  onShow() {
    this.loadMedicines()
  },
  data() {
    return {
      cabinetFindings: [],
      weekList: [
        { label: '一', done: true },
        { label: '二', done: true },
        { label: '三', done: true },
        { label: '四', done: true },
        { label: '五', done: false, isToday: true },
        { label: '六', done: false },
        { label: '日', done: false }
      ],
      medicines: [
        { name: '阿司匹林肠溶片', dose: '0.1g × 1片｜饭后服用', expire: '2027-12-10', stock: '剩15%', percent: 15, level: 'amber', theme: 'blue', risk: '库存偏低，建议补货' },
        { name: '强力枇杷露', dose: '10ml × 3次｜摇匀后服用', expire: '2026-05-20', stock: '剩80%', percent: 80, level: 'green', theme: 'teal', risk: '即将过期，优先使用' },
        { name: '多维元素片(21)', dose: '1片 × 1次｜早餐后', expire: '2028-09-15', stock: '剩60%', percent: 60, level: 'green', theme: 'indigo', risk: '' }
      ]
    }
  },
  methods: {
    async loadMedicines() {
      try {
        const items = await getMedicines()
        if (!Array.isArray(items)) return
        const inspection = await inspectCabinet(items)
        this.cabinetFindings = inspection.findings || []
        this.medicines = items.map((item, index) => {
          const percent = Math.max(0, Math.min(100, Number(item.stock) || 0))
          return {
            ...item,
            stock: `剩${percent}%`,
            percent,
            level: percent <= 20 ? 'amber' : 'green',
            theme: index % 2 ? 'teal' : 'blue'
          }
        })
      } catch (error) {
        uni.showToast({ title: error?.message || '药品加载失败', icon: 'none' })
      }
    },
    goAdd() {
      smoothNavigateTo('/pages-sub/medicine_form/medicine_form')
    },
    goOcrScan() {
      smoothNavigateTo('/pages-sub/ocr_scan/medicine_ocr')
    },
    goAiChat() {
      smoothNavigateTo('/pages-sub/ai_chat/ai_chat')
    },
    showMedTip(item) {
      uni.showModal({
        title: item.name,
        content: item.risk || '当前暂无明显风险，请继续按医嘱服药。',
        showCancel: false
      })
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
.page-content { padding: 32rpx; padding-top: calc(var(--status-bar-height) + 100rpx + 16rpx); padding-bottom: 170rpx; }
.search-box { margin-top: 32rpx; height: 92rpx; padding: 0 28rpx; display: flex; align-items: center; gap: 16rpx; border-radius: 18rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 8rpx 20rpx rgba(31, 72, 55, 0.04); }
.search-icon { font-size: 30rpx; opacity: 0.5; }
.search-input { flex: 1; font-size: 28rpx; color: #17231F; }
.med-entry-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx; margin-top: 28rpx; }
.entry-card { min-height: 140rpx; padding: 24rpx 16rpx; border-radius: 18rpx; background: #FFFFFF; box-sizing: border-box; border: 1rpx solid #DDE7E1; box-shadow: 0 8rpx 20rpx rgba(31, 72, 55, 0.04); }.entry-card.primary { background: #F0FAF6; border-color: #BFE3D6; }.entry-icon { display: block; width: 36rpx; height: 36rpx; }.entry-title { display: block; margin-top: 12rpx; font-size: 24rpx; line-height: 1.3; color: #17231F; font-weight: 700; }.entry-desc { display: block; margin-top: 10rpx; font-size: 22rpx; color: #71817A; line-height: 1.3; }
.section-card, .medicine-card { margin-top: 32rpx; padding: 32rpx; border-radius: 22rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 10rpx 24rpx rgba(31, 72, 55, 0.05); }
.section-head { display: flex; justify-content: space-between; align-items: center; }
.section-title { font-size: 32rpx; font-weight: 700; color: #17231F; }
.section-subtitle { font-size: 24rpx; color: #71817A; }
.rate-value { color: #0E9F8E; font-size: 40rpx; font-weight: 700; }
.week-row { display: flex; justify-content: space-between; margin-top: 32rpx; }
.day-item { display: flex; flex-direction: column; align-items: center; gap: 10rpx; }
.day-circle { width: 64rpx; height: 64rpx; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #E8F1ED; color: #71817A; font-size: 24rpx; font-weight: 700; }
.day-circle.done { background: #0E9F8E; color: #FFFFFF; }
.day-circle.today { background: #E1F3ED; color: #0E9F8E; }
.day-mark { font-size: 22rpx; color: #9AA8A1; }
.list-head { margin: 48rpx 4rpx 0; }
.medicine-card { display: flex; gap: 24rpx; }
.med-icon-bg { width: 96rpx; height: 96rpx; border-radius: 16rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.med-icon-bg.blue { background: rgba(56, 189, 248, 0.1); } .med-icon-bg.teal { background: rgba(34, 211, 238, 0.1); } .med-icon-bg.indigo { background: rgba(129, 140, 248, 0.1); }
.med-icon { width: 48rpx; height: 48rpx; }
.med-body { flex: 1; }
.med-title-row { display: flex; justify-content: space-between; gap: 16rpx; }
.med-name { font-size: 30rpx; font-weight: 700; color: #17231F; }
.stock-tag { flex-shrink: 0; padding: 8rpx 14rpx; border-radius: 999rpx; font-size: 22rpx; }
.stock-tag.amber { color: #B96B25; background: #FFF0DF; } .stock-tag.green { color: #0E9F8E; background: #E1F3ED; }
.med-desc, .expire-date { display: block; margin-top: 10rpx; font-size: 24rpx; color: #71817A; }
.progress-bar { height: 8rpx; margin-top: 20rpx; border-radius: 999rpx; background: #E8F1ED; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 999rpx; } .progress-fill.amber { background: #E58A3A; } .progress-fill.green { background: #36B37E; }
.risk-row { display: flex; align-items: center; gap: 10rpx; margin-top: 16rpx; }
.risk-dot { width: 28rpx; height: 28rpx; border-radius: 50%; background: rgba(239, 68, 68, 0.15); color: #EF4444; text-align: center; line-height: 28rpx; font-size: 20rpx; font-weight: 700; }
.risk-text { font-size: 24rpx; color: #EF4444; font-weight: 600; }
.med-actions { display: flex; gap: 16rpx; margin-top: 24rpx; }
.med-action { flex: 1; height: 68rpx; line-height: 68rpx; border-radius: 14rpx; border: none; background: #F4F7F5; color: #50605A; font-size: 24rpx; border: 1rpx solid #DDE7E1; }
.med-action.primary { background: #E1F3ED; color: #0E9F8E; font-weight: 700; border-color: #BFE3D6; }
</style>

<template>
  <view class="page-container">
    <view class="header-card">
      <view>
        <text class="page-title">智慧药箱</text>
        <text class="page-desc">OCR 录入药盒，AI 校验用法、禁忌和库存风险</text>
      </view>
      <button class="scan-btn" @click="goAdd">录入</button>
    </view>

    <view class="search-box">
      <text class="search-icon">🔍</text>
      <input class="search-input" placeholder="搜索药品、功效、说明书、禁忌" />
    </view>

    <view class="notice-strip">
      <image class="notice-icon" src="/static/icons/warning.png" mode="aspectFit" />
      <text class="notice-text">有 1 种药品库存偏低，1 种药品即将过期，建议优先处理。</text>
    </view>

    <view class="med-entry-grid">
      <view class="entry-card primary" @click="goAdd">
        <image class="entry-icon" src="/static/icons/plus.png" mode="aspectFit" />
        <text class="entry-title">手动录入药品</text>
        <text class="entry-desc">名称、剂量、库存</text>
      </view>
      <view class="entry-card" @click="goOcrScan">
        <image class="entry-icon" src="/static/icons/report.png" mode="aspectFit" />
        <text class="entry-title">识别药盒/说明书</text>
        <text class="entry-desc">OCR 自动提取</text>
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

    <view class="ai-tip-card">
      <text class="ai-title">AI 用药提醒</text>
      <text class="ai-text">阿司匹林存在低库存风险，建议 3 天内补货；若同时服用降压药，请按医嘱监测血压。</text>
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
    goAdd() {
      smoothNavigateTo('/pages-sub/medicine_form/medicine_form')
    },
    goOcrScan() {
      smoothNavigateTo('/pages-sub/ocr_scan/ocr_scan')
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
.page-container { min-height: 100vh; background: linear-gradient(180deg, #EEFBF7 0%, #F8FAFC 34%, #F8FAFC 100%); padding: 28rpx 28rpx 170rpx; box-sizing: border-box; }
.header-card { display: flex; justify-content: space-between; align-items: center; padding: 34rpx; border-radius: 18rpx; color: #fff; background: linear-gradient(135deg, #0F766E, #10B981); box-shadow: 0 16rpx 36rpx rgba(13,148,136,.18); }
.page-title { display: block; font-size: 40rpx; font-weight: 900; }
.page-desc { display: block; max-width: 470rpx; margin-top: 10rpx; font-size: 24rpx; line-height: 1.45; opacity: .88; }
.scan-btn { margin: 0; min-width: 112rpx; height: 68rpx; line-height: 68rpx; border-radius: 14rpx; background: #FFFFFF; color: #0F766E; font-size: 26rpx; font-weight: 900; border: none; }
.search-box { margin-top: 24rpx; height: 88rpx; padding: 0 26rpx; display: flex; align-items: center; gap: 16rpx; border-radius: 16rpx; background: #fff; box-shadow: 0 8rpx 22rpx rgba(15, 23, 42, .05); }
.search-icon { font-size: 30rpx; }
.search-input { flex: 1; font-size: 27rpx; }
.notice-strip { display: flex; align-items: flex-start; gap: 14rpx; margin-top: 22rpx; padding: 20rpx 22rpx; border-radius: 16rpx; background: #FFF7ED; border: 1rpx solid #FED7AA; }
.notice-icon { width: 32rpx; height: 32rpx; flex-shrink: 0; }.notice-text { flex: 1; font-size: 24rpx; line-height: 1.5; color: #9A3412; font-weight: 700; }
.med-entry-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx; margin-top: 22rpx; }
.entry-card { min-height: 138rpx; padding: 20rpx 14rpx; border-radius: 16rpx; background: #fff; box-shadow: 0 8rpx 22rpx rgba(15, 23, 42, .05); box-sizing: border-box; border: 1rpx solid #EEF2F7; }.entry-card.primary { background: #ECFDF5; border-color: #A7F3D0; }.entry-icon { display: block; width: 36rpx; height: 36rpx; }.entry-title { display: block; margin-top: 10rpx; font-size: 24rpx; line-height: 1.25; color: #1E293B; font-weight: 900; }.entry-desc { display: block; margin-top: 8rpx; font-size: 20rpx; color: #64748B; line-height: 1.25; }
.section-card, .medicine-card, .ai-tip-card { margin-top: 24rpx; padding: 30rpx; border: 1rpx solid #E8F0F2; border-radius: 16rpx; background: #fff; box-shadow: 0 8rpx 22rpx rgba(15, 23, 42, .05); }
.section-head { display: flex; justify-content: space-between; align-items: center; }
.section-title { font-size: 31rpx; font-weight: 900; color: #1E293B; }
.section-subtitle { font-size: 23rpx; color: #94A3B8; }
.rate-value { color: #10B981; font-size: 36rpx; font-weight: 900; }
.week-row { display: flex; justify-content: space-between; margin-top: 28rpx; }
.day-item { display: flex; flex-direction: column; align-items: center; gap: 8rpx; }
.day-circle { width: 62rpx; height: 62rpx; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #E2E8F0; color: #64748B; font-size: 24rpx; font-weight: 800; }
.day-circle.done { background: #10B981; color: #fff; }
.day-circle.today { background: #D1FAE5; color: #059669; }
.day-mark { font-size: 22rpx; color: #CBD5E1; }
.list-head { margin: 34rpx 4rpx 0; }
.medicine-card { display: flex; gap: 22rpx; }
.med-icon-bg { width: 92rpx; height: 92rpx; border-radius: 16rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.med-icon-bg.blue { background: #EFF6FF; } .med-icon-bg.teal { background: #ECFDF5; } .med-icon-bg.indigo { background: #EEF2FF; }
.med-icon { width: 46rpx; height: 46rpx; }
.med-body { flex: 1; }
.med-title-row { display: flex; justify-content: space-between; gap: 14rpx; }
.med-name { font-size: 29rpx; font-weight: 900; color: #1E293B; }
.stock-tag { flex-shrink: 0; padding: 6rpx 12rpx; border-radius: 999rpx; font-size: 22rpx; }
.stock-tag.amber { color: #D97706; background: #FFFBEB; } .stock-tag.green { color: #059669; background: #ECFDF5; }
.med-desc, .expire-date { display: block; margin-top: 8rpx; font-size: 23rpx; color: #64748B; }
.progress-bar { height: 9rpx; margin-top: 18rpx; border-radius: 999rpx; background: #E2E8F0; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 999rpx; } .progress-fill.amber { background: #FBBF24; } .progress-fill.green { background: #10B981; }
.risk-row { display: flex; align-items: center; gap: 8rpx; margin-top: 14rpx; }
.risk-dot { width: 28rpx; height: 28rpx; border-radius: 50%; background: #FFF1F2; color: #E11D48; text-align: center; line-height: 28rpx; font-size: 20rpx; font-weight: 900; }
.risk-text { font-size: 23rpx; color: #E11D48; font-weight: 700; }
.med-actions { display: flex; gap: 14rpx; margin-top: 18rpx; }
.med-action { flex: 1; height: 62rpx; line-height: 62rpx; border-radius: 14rpx; border: none; background: #F1F5F9; color: #334155; font-size: 24rpx; }
.med-action.primary { background: #ECFDF5; color: #059669; font-weight: 800; }
.ai-tip-card { background: linear-gradient(180deg, #FFFFFF, #ECFDF5); }
.ai-title { display: block; font-size: 30rpx; font-weight: 900; color: #0F766E; }
.ai-text { display: block; margin-top: 14rpx; font-size: 26rpx; line-height: 1.6; color: #334155; }
</style>

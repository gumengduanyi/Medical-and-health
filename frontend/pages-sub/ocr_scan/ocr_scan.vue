<template>
  <view class="page-container">
    <view class="custom-nav">
      <view class="status-bar"></view>
      <view class="nav-content">
        <view class="nav-back" @click="goBack"><text class="nav-back-icon">‹</text></view>
        <text class="nav-title">{{ pageTitle }}</text>
        <view class="nav-placeholder"></view>
      </view>
    </view>

    <view class="page-content" :class="{ 'has-result': scanResult }">
    <text class="page-desc">{{ pageDesc }}</text>

    <view class="scan-card">
      <view class="scan-frame">
        <view class="corner top-left"></view><view class="corner top-right"></view>
        <view class="corner bottom-left"></view><view class="corner bottom-right"></view>
        <image class="scan-image" :src="isMedicineMode ? '/static/icons/pill.png' : '/static/icons/report.png'" mode="aspectFit" />
      </view>
      <text class="scan-title">{{ scanTitle }}</text>
      <text class="scan-desc">{{ scanDesc }}</text>
      <view class="scan-actions">
        <template v-if="isMedicineMode">
          <view class="scan-btn primary" @click="chooseAndScan('medicine', '药品信息')">拍摄药盒或说明书</view>
        </template>
        <template v-else>
          <view class="scan-btn primary" @click="chooseAndScan('report', '体检报告')">体检报告</view>
          <view class="scan-btn" @click="chooseAndScan('diagnosis', '诊断记录')">诊断记录</view>
          <view class="scan-btn" @click="chooseAndScan('lab', '化验单')">化验单</view>
        </template>
      </view>
    </view>

    <view class="result-card" v-if="scanResult">
      <view class="section-head">
        <text class="section-title">识别预览</text>
        <text class="confidence">置信度 {{ confidence }}%</text>
      </view>
      <view class="result-meta">
        <text class="result-meta-label">资料类型</text>
        <text class="result-meta-value">{{ sourceLabel }}</text>
      </view>
      <scroll-view class="table-scroll" scroll-x="true" show-scrollbar="false">
        <view class="ocr-table" :class="{ medicine: isMedicineMode }">
          <view v-if="!isMedicineMode" class="table-row table-head">
            <text class="table-cell name">指标名称</text>
            <text class="table-cell value">检测值</text>
            <text class="table-cell unit">单位</text>
            <text class="table-cell reference">参考范围</text>
            <text class="table-cell status">状态</text>
          </view>
          <view v-else class="table-row table-head medicine-table-head">
            <text class="table-cell medicine-name">信息项</text>
            <text class="table-cell medicine-value">识别结果</text>
            <text class="table-cell medicine-status">状态</text>
          </view>
          <view v-if="!isMedicineMode" class="table-row" :class="{ warning: item.status === 'warning' }" v-for="(item, index) in scanResult" :key="item.label + index">
            <text class="table-cell name">{{ item.label }}</text>
            <text class="table-cell value">{{ item.value }}</text>
            <text class="table-cell unit">{{ item.unit || '-' }}</text>
            <text class="table-cell reference">{{ item.reference || '-' }}</text>
            <text class="table-cell status" :class="item.status">{{ item.status === 'warning' ? '需关注' : item.status === 'pending' ? '待确认' : '正常' }}</text>
          </view>
          <view v-else class="table-row medicine-table-row" v-for="(item, index) in scanResult" :key="item.label + index">
            <text class="table-cell medicine-name">{{ item.label }}</text>
            <text class="table-cell medicine-value">{{ item.value }}</text>
            <text class="table-cell medicine-status" :class="item.status">{{ item.status === 'pending' ? '待确认' : '已识别' }}</text>
          </view>
        </view>
      </scroll-view>
      <view class="notice-box">{{ noticeText }}</view>
    </view>
    </view>

    <view v-if="scanResult" class="result-action-bar">
      <view class="action-btn secondary" @click="chooseAndScan(sourceType, sourceLabel)">重新识别</view>
      <view class="action-btn primary" @click="saveResult">{{ isSubmitting ? '入库中...' : '确认入库' }}</view>
    </view>
  </view>
</template>

<script>
import { confirmOcrResult, scanMedicine, scanReport } from '@/services/modules/ocr.service.js'

export default {
  props: {
    mode: { type: String, default: 'report' }
  },
  data() {
    return {
      pageMode: this.mode === 'medicine' ? 'medicine' : 'report',
      isSubmitting: false,
      sourceType: this.mode === 'medicine' ? 'medicine' : 'report',
      sourceLabel: this.mode === 'medicine' ? '药品信息' : '体检报告',
      confidence: 0,
      scanResult: null,
      rawFields: [],
      rawTexts: [],
      storedFile: ''
    }
  },
  onLoad(options = {}) {
    const requestedMode = options.mode || this.mode
    this.pageMode = requestedMode === 'medicine' ? 'medicine' : 'report'
    this.sourceType = this.isMedicineMode ? 'medicine' : 'report'
    this.sourceLabel = this.isMedicineMode ? '药品信息' : '体检报告'
  },
  computed: {
    isMedicineMode() { return this.mode === 'medicine' || this.pageMode === 'medicine' },
    pageTitle() { return this.isMedicineMode ? '药箱 OCR 录入' : '档案 OCR 录入' },
    pageDesc() { return this.isMedicineMode ? '拍摄药盒或说明书，识别药品名称、用法和有效期。' : '拍摄体检报告、诊断证明或化验单，识别后先核对再入库。' },
    scanTitle() { return this.isMedicineMode ? '识别药品资料' : '选择识别资料类型' },
    scanDesc() { return this.isMedicineMode ? '建议拍摄完整药盒或说明书，确保药品名称、规格和有效期清晰可见。' : '建议保持文字完整、光线充足，识别完成后请手动确认关键指标。' },
    noticeText() { return this.isMedicineMode ? '请重点核对药品名称、规格、用法和有效期。确认后会同步到智慧药箱。' : '请重点核对异常指标、日期和医院名称。确认后会同步到健康档案。' }
  },
  methods: {
    goBack() { uni.navigateBack() },
    chooseAndScan(type, label) {
      this.sourceType = type
      this.sourceLabel = label
      uni.chooseImage({
        count: 1,
        sourceType: ['album', 'camera'],
        success: async (res) => {
          const filePath = res.tempFilePaths[0]
          uni.showLoading({ title: '识别中' })
          try {
            const result = type === 'medicine'
              ? await scanMedicine(filePath, { source_type: type })
              : await scanReport(filePath, { source_type: type })
            this.applyScanResult(result)
            uni.showToast({ title: '识别完成', icon: 'success' })
          } catch (error) {
            uni.showToast({ title: error?.message || '识别失败', icon: 'none' })
          } finally {
            uni.hideLoading()
          }
        }
      })
    },
    applyScanResult(result) {
      this.confidence = result.confidence || 0
      this.rawFields = Array.isArray(result.fields) ? result.fields : []
      this.rawTexts = Array.isArray(result.texts) ? result.texts : []
      this.storedFile = result.storedFile || ''
      this.scanResult = this.rawFields.map((item) => ({
        label: item.label || item.name || '字段',
        value: item.value || '',
        unit: item.unit || '',
        reference: item.reference || '',
        status: item.status || 'normal'
      }))
      if (!this.scanResult.length && this.rawTexts.length) {
        this.scanResult = this.rawTexts.slice(0, 8).map((value, index) => ({
          label: `文本 ${index + 1}`,
          value,
          unit: '',
          reference: '',
          status: 'pending'
        }))
      }
    },
    async saveResult() {
      if (this.isSubmitting) return
      this.isSubmitting = true
      uni.showLoading({ title: '入库中' })
      try {
        const title = this.sourceType === 'medicine' ? 'OCR 药品确认' : 'OCR 体检报告确认'
        await confirmOcrResult({
          sourceType: this.sourceType,
          title,
          fields: this.rawFields,
          texts: this.rawTexts,
          storedFile: this.storedFile
        })
        uni.showToast({ title: '已入库', icon: 'success' })
        setTimeout(() => uni.navigateBack(), 500)
      } catch (error) {
        uni.showToast({ title: error?.message || '入库失败', icon: 'none' })
      } finally {
        this.isSubmitting = false
        uni.hideLoading()
      }
    }
  }
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: #F4F7F5; }
.custom-nav { position: fixed; top: 0; left: 0; right: 0; z-index: 999; background: rgba(244, 247, 245, 0.92); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-bottom: 1rpx solid #DDE7E1; }
.status-bar { height: var(--status-bar-height); }
.nav-content { height: 100rpx; padding: 0 32rpx; display: flex; align-items: center; justify-content: space-between; }
.nav-back { width: 60rpx; height: 60rpx; display: flex; align-items: center; justify-content: center; }
.nav-back-icon { font-size: 56rpx; color: #17231F; font-weight: 300; line-height: 1; }
.nav-placeholder { width: 60rpx; }
.nav-title { position: absolute; left: 50%; transform: translateX(-50%); font-size: 36rpx; font-weight: 700; color: #17231F; }
.page-content { padding: 32rpx; padding-top: calc(var(--status-bar-height) + 100rpx + 32rpx); padding-bottom: 80rpx; }
.page-content.has-result { padding-bottom: 190rpx; }
.page-desc { display: block; font-size: 26rpx; color: #71817A; line-height: 1.6; }

.scan-card, .result-card { margin-top: 32rpx; padding: 32rpx; border-radius: 22rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 10rpx 24rpx rgba(31, 72, 55, 0.05); }
.scan-frame { position: relative; width: 100%; height: 280rpx; border-radius: 16rpx; background: #F0FAF6; display: flex; align-items: center; justify-content: center; }
.scan-image { width: 88rpx; height: 88rpx; opacity: 0.6; }.corner { position: absolute; width: 46rpx; height: 46rpx; border-color: #0E9F8E; border-style: solid; }.top-left { left: 26rpx; top: 26rpx; border-width: 6rpx 0 0 6rpx; }.top-right { right: 26rpx; top: 26rpx; border-width: 6rpx 6rpx 0 0; }.bottom-left { left: 26rpx; bottom: 26rpx; border-width: 0 0 6rpx 6rpx; }.bottom-right { right: 26rpx; bottom: 26rpx; border-width: 0 6rpx 6rpx 0; }
.scan-title { display: block; margin-top: 28rpx; font-size: 32rpx; color: #17231F; font-weight: 700; }.scan-desc { display: block; margin-top: 12rpx; font-size: 25rpx; color: #71817A; line-height: 1.55; }
.scan-actions { display: grid; gap: 16rpx; margin-top: 28rpx; }.scan-btn, .save-btn { height: 84rpx; display: flex; align-items: center; justify-content: center; border-radius: 14rpx; background: #F4F7F5; color: #50605A; font-size: 28rpx; font-weight: 600; border: 1rpx solid #DDE7E1; }.scan-btn.primary, .save-btn { background: #0E9F8E; color: #FFFFFF; border-color: #0E9F8E; font-weight: 700; }
.section-head { display: flex; justify-content: space-between; align-items: center; gap: 20rpx; }.section-title { font-size: 30rpx; color: #17231F; font-weight: 700; }.confidence { padding: 8rpx 14rpx; border-radius: 999rpx; background: #E1F3ED; color: #0E9F8E; font-size: 22rpx; font-weight: 700; }
.result-meta { display: flex; justify-content: space-between; align-items: center; margin-top: 24rpx; padding-bottom: 20rpx; border-bottom: 1rpx solid #E8F1ED; }.result-meta-label { color: #71817A; font-size: 25rpx; }.result-meta-value { color: #17231F; font-size: 25rpx; font-weight: 700; }
.table-scroll { width: 100%; margin-top: 12rpx; }
.ocr-table { min-width: 1080rpx; }
.ocr-table.medicine { min-width: 860rpx; }.medicine-name { width: 300rpx; color: #17231F; }.medicine-value { width: 430rpx; color: #17231F; }.medicine-status { width: 130rpx; text-align: center; color: #187A83; font-weight: 600; }.medicine-table-head .table-cell { color: #187A83; }.medicine-table-row { min-height: 92rpx; }
.table-row { display: flex; align-items: center; min-height: 82rpx; border-bottom: 1rpx solid #E8F1ED; }.table-row.warning { background: #FFF9F1; }.table-head { min-height: 68rpx; background: #F0FAF6; border-radius: 10rpx; border-bottom: none; }.table-cell { flex-shrink: 0; padding: 18rpx 14rpx; box-sizing: border-box; color: #50605A; font-size: 23rpx; line-height: 1.35; word-break: break-all; }.table-cell.name { width: 360rpx; color: #17231F; }.table-cell.value { width: 170rpx; font-weight: 700; color: #17231F; }.table-cell.unit { width: 160rpx; }.table-cell.reference { width: 230rpx; }.table-cell.status { width: 140rpx; text-align: center; color: #36B37E; font-weight: 600; }.table-head .table-cell { padding-top: 14rpx; padding-bottom: 14rpx; color: #0E9F8E; font-size: 22rpx; font-weight: 700; }.table-row.warning .table-cell.value, .table-cell.status.warning { color: #C56F20; }.table-cell.status.pending { color: #9A7A3A; }
.notice-box { margin-top: 22rpx; padding: 24rpx; border-radius: 14rpx; background: #FFF7ED; color: #B96B25; font-size: 24rpx; line-height: 1.5; border: 1rpx solid #F3D8B7; }
.result-action-bar { position: fixed; left: 0; right: 0; bottom: 0; z-index: 998; display: flex; gap: 16rpx; padding: 18rpx 32rpx calc(18rpx + env(safe-area-inset-bottom)); background: rgba(255, 255, 255, 0.96); border-top: 1rpx solid #DDE7E1; box-shadow: 0 -8rpx 24rpx rgba(31, 72, 55, 0.08); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); }
.action-btn { flex: 1; height: 84rpx; display: flex; align-items: center; justify-content: center; border-radius: 14rpx; font-size: 28rpx; font-weight: 700; }.action-btn.secondary { color: #50605A; background: #F4F7F5; border: 1rpx solid #DDE7E1; }.action-btn.primary { color: #FFFFFF; background: #0E9F8E; border: 1rpx solid #0E9F8E; }
</style>

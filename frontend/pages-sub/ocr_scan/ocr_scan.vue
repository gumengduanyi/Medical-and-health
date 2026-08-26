<template>
  <view class="page-container">
    <view class="header-card">
      <view>
        <text class="page-title">OCR 报告识别</text>
        <text class="page-desc">拍摄体检报告、诊断证明或化验单，识别后先核对再入库。</text>
      </view>
      <view class="header-icon-wrap"><image class="header-icon" src="/static/icons/report.png" mode="aspectFit" /></view>
    </view>

    <view class="scan-card">
      <view class="scan-frame">
        <view class="corner top-left"></view><view class="corner top-right"></view>
        <view class="corner bottom-left"></view><view class="corner bottom-right"></view>
        <image class="scan-image" src="/static/icons/report.png" mode="aspectFit" />
      </view>
      <text class="scan-title">选择识别资料类型</text>
      <text class="scan-desc">建议保持文字完整、光线充足，识别完成后请手动确认关键指标。</text>
      <view class="scan-actions">
        <button class="scan-btn primary" @click="chooseAndScan('report', '体检报告')">体检报告</button>
        <button class="scan-btn" @click="chooseAndScan('diagnosis', '诊断记录')">诊断记录</button>
        <button class="scan-btn" @click="chooseAndScan('lab', '化验单')">化验单</button>
        <button class="scan-btn" @click="chooseAndScan('medicine', '药品信息')">药品信息</button>
      </view>
    </view>

    <view class="result-card" v-if="scanResult">
      <view class="section-head">
        <text class="section-title">识别预览</text>
        <text class="confidence">置信度 {{ confidence }}%</text>
      </view>
      <view class="result-row">
        <text class="result-label">资料类型</text>
        <text class="result-value">{{ sourceLabel }}</text>
      </view>
      <view class="result-row" v-for="item in scanResult" :key="item.label">
        <text class="result-label">{{ item.label }}</text>
        <text class="result-value">{{ item.value }}</text>
      </view>
      <view class="notice-box">请重点核对异常指标、日期和医院名称。确认后会同步到健康档案。</view>
      <button class="save-btn" @click="saveResult">确认入库</button>
    </view>
  </view>
</template>

<script>
import { confirmOcrResult, scanMedicine, scanReport } from '@/services/modules/ocr.service.js'

export default {
  data() {
    return {
      isSubmitting: false,
      sourceType: 'report',
      sourceLabel: '体检报告',
      confidence: 0,
      scanResult: null,
      rawFields: [],
      rawTexts: [],
      storedFile: ''
    }
  },
  methods: {
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
        value: item.value || ''
      }))
      if (!this.scanResult.length && this.rawTexts.length) {
        this.scanResult = this.rawTexts.slice(0, 8).map((value, index) => ({
          label: `文本 ${index + 1}`,
          value
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
.page-container { min-height: 100vh; padding: 28rpx 28rpx 80rpx; background: linear-gradient(180deg, #EEF2FF 0%, #F8FAFC 34%, #F8FAFC 100%); box-sizing: border-box; }
.header-card { display: flex; justify-content: space-between; align-items: center; gap: 20rpx; padding: 36rpx; border-radius: 18rpx; color: #fff; background: linear-gradient(135deg, #2563EB, #0F766E); box-shadow: 0 16rpx 36rpx rgba(37,99,235,.18); }
.page-title { display: block; font-size: 40rpx; font-weight: 900; }.page-desc { display: block; margin-top: 10rpx; font-size: 24rpx; line-height: 1.5; opacity: .9; }.header-icon-wrap { width: 86rpx; height: 86rpx; border-radius: 16rpx; background: rgba(255,255,255,.18); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }.header-icon { width: 48rpx; height: 48rpx; }
.scan-card, .result-card { margin-top: 24rpx; padding: 32rpx; border-radius: 16rpx; background: #fff; box-shadow: 0 8rpx 22rpx rgba(15,23,42,.05); }
.scan-frame { position: relative; width: 100%; height: 280rpx; border-radius: 16rpx; background: linear-gradient(135deg, #F8FAFC, #EFF6FF); display: flex; align-items: center; justify-content: center; }
.scan-image { width: 88rpx; height: 88rpx; }.corner { position: absolute; width: 46rpx; height: 46rpx; border-color: #0F766E; border-style: solid; }.top-left { left: 26rpx; top: 26rpx; border-width: 6rpx 0 0 6rpx; }.top-right { right: 26rpx; top: 26rpx; border-width: 6rpx 6rpx 0 0; }.bottom-left { left: 26rpx; bottom: 26rpx; border-width: 0 0 6rpx 6rpx; }.bottom-right { right: 26rpx; bottom: 26rpx; border-width: 0 6rpx 6rpx 0; }
.scan-title { display: block; margin-top: 28rpx; font-size: 32rpx; color: #1E293B; font-weight: 900; }.scan-desc { display: block; margin-top: 12rpx; font-size: 25rpx; color: #64748B; line-height: 1.55; }
.scan-actions { display: grid; gap: 16rpx; margin-top: 26rpx; }.scan-btn, .save-btn { height: 84rpx; line-height: 84rpx; border-radius: 14rpx; border: none; background: #F1F5F9; color: #334155; font-size: 28rpx; font-weight: 800; }.scan-btn.primary, .save-btn { background: #0F766E; color: #fff; }
.section-head { display: flex; justify-content: space-between; align-items: center; gap: 20rpx; }.section-title { font-size: 31rpx; color: #1E293B; font-weight: 900; }.confidence { padding: 6rpx 12rpx; border-radius: 999rpx; background: #EFF6FF; color: #2563EB; font-size: 22rpx; font-weight: 800; }
.result-row { display: flex; justify-content: space-between; gap: 20rpx; padding: 22rpx 0; border-bottom: 1rpx solid #E2E8F0; }.result-label { color: #64748B; font-size: 25rpx; }.result-value { color: #1E293B; font-size: 25rpx; font-weight: 800; text-align: right; }.notice-box { margin-top: 22rpx; padding: 20rpx; border-radius: 14rpx; background: #FFF7ED; color: #9A3412; font-size: 24rpx; line-height: 1.5; }.save-btn { margin-top: 24rpx; }
</style>

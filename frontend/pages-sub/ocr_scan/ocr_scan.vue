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

    <view class="page-content" :class="{ 'with-action-bar': !isMedicineMode || scanResult }">
      <!-- 档案智能录入 -->
      <template v-if="!isMedicineMode">
        <text class="page-desc">填写报告信息并上传图片，识别后核对再入库。</text>

        <view class="form-card">
          <text class="section-title">基本信息</text>
          <view class="form-row">
            <text class="form-label">名称</text>
            <input class="form-input" v-model="form.name" maxlength="50" placeholder="例：医院+原因" placeholder-class="form-placeholder" />
          </view>
          <view class="form-row">
            <text class="form-label">类别</text>
            <view class="form-value-wrap" @click="openCategoryPicker">
              <text class="form-value">{{ categories[categoryIndex] }}</text>
              <text class="form-arrow">›</text>
            </view>
          </view>
          <view class="form-row">
            <text class="form-label">录入时间</text>
            <view class="datetime-row">
              <view class="datetime-pill" @click="openDatePicker('entryDate')">{{ form.entryDate }}</view>
              <view class="datetime-pill" @click="openTimePicker('entryTime')">{{ form.entryTime }}</view>
            </view>
          </view>
          <view class="form-row">
            <text class="form-label">报告时间</text>
            <view class="datetime-row">
              <view class="datetime-pill" @click="openDatePicker('reportDate')">{{ form.reportDate }}</view>
              <view class="datetime-pill" @click="openTimePicker('reportTime')">{{ form.reportTime }}</view>
            </view>
          </view>
        </view>

        <view class="form-card">
          <view class="section-head">
            <text class="section-title">图片</text>
            <text class="section-tip">支持拍照或从相册选择</text>
          </view>
          <view class="pick-grid">
            <view class="pick-block" hover-class="pick-block-hover" @click="pickImage('camera')">
              <view class="anim-icon cam">
                <view class="cam-body">
                  <view class="cam-top"></view>
                  <view class="cam-lens"></view>
                  <view class="cam-flash"></view>
                </view>
              </view>
              <text class="pick-label">拍摄</text>
            </view>
            <view class="pick-block" hover-class="pick-block-hover" @click="pickImage('album')">
              <view class="anim-icon photo">
                <view class="photo-frame">
                  <view class="photo-sun"></view>
                  <view class="photo-hill"></view>
                  <view class="photo-hill second"></view>
                </view>
              </view>
              <text class="pick-label">上传图片</text>
            </view>
          </view>
          <view v-if="images.length" class="image-grid">
            <view v-for="(item, index) in images" :key="item.key" class="image-item">
              <image class="image-thumb" :src="item.preview" mode="aspectFill" @click="previewImage(index)" />
              <view v-if="item.uploading" class="image-mask"><text class="image-mask-text">上传中</text></view>
              <view class="image-remove" @click.stop="removeImage(index)">×</view>
            </view>
          </view>
        </view>

        <view class="form-card">
          <view class="section-head">
            <text class="section-title">报告文件</text>
            <text class="add-file-btn" @click="pickFile">+ 添加文件</text>
          </view>
          <view v-if="files.length" class="file-list">
            <view v-for="(item, index) in files" :key="item.key" class="file-item">
              <view class="file-main" @click="openFile(item)">
                <text class="file-name">{{ item.name }}</text>
                <text class="file-meta">{{ item.uploading ? '上传中...' : item.sizeText }}</text>
              </view>
              <text class="file-delete" @click.stop="removeFile(index)">删除</text>
            </view>
          </view>
          <text v-else class="empty-tip">暂未添加报告文件</text>
        </view>
      </template>

      <!-- 药箱智能录入 -->
      <template v-else>
        <text class="page-desc">{{ pageDesc }}</text>

        <view class="scan-card">
          <view class="scan-frame">
            <view class="corner top-left"></view><view class="corner top-right"></view>
            <view class="corner bottom-left"></view><view class="corner bottom-right"></view>
            <image class="scan-image" src="/static/icons/pill.png" mode="aspectFit" />
          </view>
          <text class="scan-title">{{ scanTitle }}</text>
          <text class="scan-desc">{{ scanDesc }}</text>
          <view class="scan-actions">
            <view class="scan-btn primary" @click="chooseAndScan('medicine', '药品信息')">拍摄药盒或说明书</view>
          </view>
        </view>
      </template>

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

      <view v-if="isMedicineMode && leafletCandidate" class="leaflet-card">
        <view class="section-head">
          <text class="section-title">百度百科智能体结果</text>
          <text class="confidence" :class="{ blocked: leafletCandidate.status !== 'candidate' }">
            {{ leafletCandidate.status === 'candidate' ? `置信度 ${Math.round((leafletCandidate.confidence || 0) * 100)}%` : '需人工处理' }}
          </text>
        </view>
        <text class="leaflet-source">来源：百度百科浏览器可见页面</text>
        <view v-for="name in leafletSectionNames" :key="name" class="leaflet-section">
          <text class="leaflet-section-title">{{ name }}</text>
          <text class="leaflet-section-content">{{ leafletCandidate.sections && leafletCandidate.sections[name] ? leafletCandidate.sections[name] : '未找到该章节' }}</text>
        </view>
        <view class="notice-box leaflet-notice">{{ leafletCandidate.reason }}</view>
      </view>
    </view>

    <view v-if="picker.visible" class="picker-mask" @click="closePicker">
      <view class="picker-sheet" @click.stop>
        <view class="picker-header">
          <text class="picker-cancel" @click="closePicker">取消</text>
          <text class="picker-title">{{ picker.title }}</text>
          <text class="picker-confirm" @click="confirmPicker">确定</text>
        </view>
        <view class="picker-columns">
          <view v-for="(column, columnIndex) in picker.columns" :key="`${pickerToken}_${columnIndex}`" class="wheel-column-wrap">
            <scroll-view
              class="wheel-column"
              scroll-y
              :scroll-top="wheelTops[columnIndex]"
              :scroll-with-animation="wheelAnimating"
              @scroll="onWheelScroll(columnIndex, $event)"
            >
              <view class="wheel-pad"></view>
              <view
                v-for="(option, optionIndex) in column"
                :key="option"
                class="wheel-item"
                :class="{ active: picker.indexes[columnIndex] === optionIndex }"
              >{{ option }}</view>
              <view class="wheel-pad"></view>
            </scroll-view>
          </view>
        </view>
      </view>
    </view>

    <view v-if="!isMedicineMode || scanResult" class="result-action-bar">
      <template v-if="isMedicineMode">
        <view class="action-btn secondary" @click="chooseAndScan('medicine', '药品信息')">重新识别</view>
        <view class="action-btn primary" @click="saveResult">{{ isSubmitting ? '入库中...' : '确认入库' }}</view>
      </template>
      <view v-else class="action-btn primary" @click="submitReport">{{ isSubmitting ? '提交中...' : '确认上传' }}</view>
    </view>
  </view>
</template>

<script>
import { API_CONFIG } from '@/config/api.config.js'
import { confirmOcrResult, scanMedicine, scanReport } from '@/services/modules/ocr.service.js'
import { submitReport as submitReportApi } from '@/services/modules/health.service.js'
import { uploadPhoto, uploadReportFile } from '@/services/modules/upload.service.js'

const CATEGORIES = ['体检报告', '门诊报告', '住院报告', '急诊报告', '其他报告']

function pad(value) {
  return String(value).padStart(2, '0')
}

function nowParts() {
  const now = new Date()
  return {
    date: `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`,
    time: `${pad(now.getHours())}:${pad(now.getMinutes())}`
  }
}

export default {
  props: {
    mode: { type: String, default: 'report' }
  },
  data() {
    const now = nowParts()
    return {
      pageMode: this.mode === 'medicine' ? 'medicine' : 'report',
      isSubmitting: false,
      sourceType: this.mode === 'medicine' ? 'medicine' : 'report',
      sourceLabel: this.mode === 'medicine' ? '药品信息' : CATEGORIES[0],
      confidence: 0,
      scanResult: null,
      rawFields: [],
      rawTexts: [],
      storedFile: '',
      outputDir: '',
      leafletCandidate: null,
      categories: CATEGORIES,
      categoryIndex: 0,
      form: {
        name: '',
        entryDate: now.date,
        entryTime: now.time,
        reportDate: now.date,
        reportTime: now.time
      },
      images: [],
      files: [],
      pickerToken: 0,
      wheelTops: [0, 0, 0],
      wheelAnimating: false,
      picker: {
        visible: false,
        mode: 'selector',
        title: '',
        target: '',
        columns: [],
        indexes: [0, 0, 0]
      }
    }
  },
  created() {
    this.itemHeightPx = uni.upx2px(92)
    this.snapTimers = {}
  },
  onLoad(options = {}) {
    const requestedMode = options.mode || this.mode
    this.pageMode = requestedMode === 'medicine' ? 'medicine' : 'report'
    this.sourceType = this.isMedicineMode ? 'medicine' : 'report'
    this.sourceLabel = this.isMedicineMode ? '药品信息' : this.categories[this.categoryIndex]
    if (!this.isMedicineMode) {
      const now = nowParts()
      this.form.entryDate = now.date
      this.form.entryTime = now.time
    }
  },
  computed: {
    isMedicineMode() { return this.mode === 'medicine' || this.pageMode === 'medicine' },
    pageTitle() { return this.isMedicineMode ? '药箱智能录入' : '档案智能录入' },
    pageDesc() { return this.isMedicineMode ? '拍摄药盒或说明书，识别药品名称、用法和有效期。' : '拍摄体检报告、诊断证明或化验单，识别后先核对再入库。' },
    scanTitle() { return this.isMedicineMode ? '识别药品资料' : '选择识别资料类型' },
    scanDesc() { return this.isMedicineMode ? '建议拍摄完整药盒或说明书，确保药品名称、规格和有效期清晰可见。' : '建议保持文字完整、光线充足，识别完成后请手动确认关键指标。' },
    noticeText() { return this.isMedicineMode ? '请重点核对药品名称、规格、用法和有效期。确认后会同步到智慧药箱。' : '请重点核对异常指标、日期和医院名称。确认后会同步到健康档案。' },
    leafletSectionNames() { return ['作用功效', '用法用量', '禁忌'] }
  },
  methods: {
    goBack() { uni.navigateBack() },
    openCategoryPicker() {
      this.pickerToken += 1
      this.picker = {
        visible: true,
        mode: 'selector',
        title: '选择类别',
        target: 'category',
        columns: [this.categories],
        indexes: [this.categoryIndex, 0, 0]
      }
      this.initWheelPosition()
    },
    openDatePicker(target) {
      const value = target === 'entryDate' ? this.form.entryDate : this.form.reportDate
      const [year, month, day] = String(value).split('-').map(Number)
      const currentYear = new Date().getFullYear()
      const years = []
      for (let item = currentYear - 20; item <= currentYear; item += 1) years.push(String(item))
      const months = Array.from({ length: 12 }, (_, index) => pad(index + 1))
      const yearIndex = Math.max(years.indexOf(String(year)), 0)
      const monthIndex = Math.max(months.indexOf(pad(month || 1)), 0)
      const days = this.buildDays(Number(years[yearIndex]), Number(months[monthIndex]))
      const dayIndex = Math.min(Math.max((day || 1) - 1, 0), days.length - 1)
      this.pickerToken += 1
      this.picker = {
        visible: true,
        mode: 'date',
        title: '选择日期',
        target,
        columns: [years, months, days],
        indexes: [yearIndex, monthIndex, dayIndex]
      }
      this.initWheelPosition()
    },
    openTimePicker(target) {
      const value = target === 'entryTime' ? this.form.entryTime : this.form.reportTime
      const [hour, minute] = String(value).split(':').map(Number)
      const hours = Array.from({ length: 24 }, (_, index) => pad(index))
      const minutes = Array.from({ length: 60 }, (_, index) => pad(index))
      this.pickerToken += 1
      this.picker = {
        visible: true,
        mode: 'time',
        title: '选择时间',
        target,
        columns: [hours, minutes],
        indexes: [Math.min(Math.max(hour || 0, 0), 23), Math.min(Math.max(minute || 0, 0), 59)]
      }
      this.initWheelPosition()
    },
    buildDays(year, month) {
      const total = new Date(year, month, 0).getDate()
      return Array.from({ length: total }, (_, index) => pad(index + 1))
    },
    onWheelScroll(columnIndex, event) {
      const column = this.picker.columns[columnIndex] || []
      if (!column.length) return
      const scrollTop = (event && event.detail ? event.detail.scrollTop : 0) || 0
      const index = Math.min(Math.max(Math.round(scrollTop / this.itemHeightPx), 0), column.length - 1)
      if (index !== this.picker.indexes[columnIndex]) this.applyWheelIndex(columnIndex, index)
      if (this.snapTimers[columnIndex]) clearTimeout(this.snapTimers[columnIndex])
      this.snapTimers[columnIndex] = setTimeout(() => {
        this.wheelAnimating = true
        this.wheelTops[columnIndex] = this.picker.indexes[columnIndex] * this.itemHeightPx
      }, 160)
    },
    applyWheelIndex(columnIndex, index) {
      const indexes = this.picker.indexes.slice()
      indexes[columnIndex] = index
      if (this.picker.mode === 'date' && columnIndex < 2) {
        const year = Number(this.picker.columns[0][indexes[0]])
        const month = Number(this.picker.columns[1][indexes[1]])
        const days = this.buildDays(year, month)
        if (days.length !== this.picker.columns[2].length) {
          this.picker.columns = [this.picker.columns[0], this.picker.columns[1], days]
          indexes[2] = Math.min(indexes[2], days.length - 1)
          this.$nextTick(() => {
            this.wheelTops[2] = indexes[2] * this.itemHeightPx
          })
        }
      }
      this.picker.indexes = indexes
    },
    initWheelPosition() {
      this.wheelAnimating = false
      this.wheelTops = [0, 0, 0]
      this.$nextTick(() => {
        setTimeout(() => {
          this.picker.indexes.forEach((index, columnIndex) => {
            this.wheelTops[columnIndex] = index * this.itemHeightPx
          })
        }, 30)
      })
    },
    confirmPicker() {
      const { target, columns, indexes } = this.picker
      if (target === 'category') {
        this.categoryIndex = indexes[0]
        this.sourceLabel = this.categories[this.categoryIndex]
      } else if (target === 'entryDate' || target === 'reportDate') {
        this.form[target] = `${columns[0][indexes[0]]}-${columns[1][indexes[1]]}-${columns[2][indexes[2]]}`
      } else {
        this.form[target] = `${columns[0][indexes[0]]}:${columns[1][indexes[1]]}`
      }
      this.closePicker()
    },
    closePicker() {
      Object.keys(this.snapTimers).forEach((key) => clearTimeout(this.snapTimers[key]))
      this.snapTimers = {}
      this.picker.visible = false
    },
    pickImage(sourceType) {
      uni.chooseImage({
        count: sourceType === 'camera' ? 1 : 9,
        sourceType: [sourceType],
        success: (res) => this.handlePickedImages(res.tempFilePaths || []),
        fail: (error) => {
          if (/deny|permission/i.test((error && error.errMsg) || '')) {
            uni.showToast({ title: '请在系统设置中开启权限', icon: 'none' })
          }
        }
      })
    },
    async handlePickedImages(filePaths) {
      for (const filePath of filePaths) {
        await this.addImage(filePath)
      }
    },
    async addImage(filePath) {
      const item = {
        key: `${Date.now()}_${Math.random().toString(16).slice(2)}`,
        preview: filePath,
        url: '',
        uploading: true
      }
      this.images.push(item)
      try {
        const result = await uploadPhoto(filePath)
        item.url = this.toFullUrl(result && result.url)
      } catch (error) {
        this.images = this.images.filter((image) => image.key !== item.key)
        uni.showToast({ title: (error && error.message) || '图片上传失败', icon: 'none' })
        return
      } finally {
        item.uploading = false
      }
      if (!this.scanResult) this.runReportScan(filePath)
    },
    previewImage(index) {
      const urls = this.images.map((item) => item.preview)
      uni.previewImage({ urls, current: urls[index] })
    },
    removeImage(index) {
      this.images.splice(index, 1)
    },
    pickFile() {
      // #ifdef MP-WEIXIN
      wx.chooseMessageFile({
        count: 1,
        type: 'file',
        success: (res) => {
          const file = (res.tempFiles || [])[0]
          if (file) this.addFile(file.path, file.name, file.size)
        }
      })
      // #endif
      // #ifndef MP-WEIXIN
      uni.chooseFile({
        count: 1,
        success: (res) => {
          const file = (res.tempFiles || [])[0]
          const filePath = (res.tempFilePaths || [])[0]
          if (file || filePath) this.addFile((file && file.path) || filePath, file && file.name, file && file.size)
        },
        fail: () => uni.showToast({ title: '当前环境暂不支持选择文件', icon: 'none' })
      })
      // #endif
    },
    async addFile(filePath, name, size) {
      const item = {
        key: `${Date.now()}_${Math.random().toString(16).slice(2)}`,
        name: name || '报告文件',
        size: size || 0,
        sizeText: this.formatSize(size),
        url: '',
        uploading: true
      }
      this.files.push(item)
      try {
        const result = await uploadReportFile(filePath)
        item.url = this.toFullUrl(result && result.url)
      } catch (error) {
        this.files = this.files.filter((file) => file.key !== item.key)
        uni.showToast({ title: (error && error.message) || '文件上传失败', icon: 'none' })
      } finally {
        item.uploading = false
      }
    },
    removeFile(index) {
      this.files.splice(index, 1)
    },
    openFile(item) {
      if (!item.url) {
        uni.showToast({ title: '文件正在上传，请稍候', icon: 'none' })
        return
      }
      // #ifdef H5
      window.open(item.url)
      // #endif
      // #ifndef H5
      uni.downloadFile({
        url: item.url,
        success: (res) => {
          uni.openDocument({
            filePath: res.tempFilePath,
            showMenu: true,
            fail: () => uni.showToast({ title: '暂不支持预览该文件', icon: 'none' })
          })
        },
        fail: () => uni.showToast({ title: '文件下载失败', icon: 'none' })
      })
      // #endif
    },
    formatSize(size) {
      if (!size) return '未知大小'
      if (size < 1024) return `${size} B`
      if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
      return `${(size / 1024 / 1024).toFixed(1)} MB`
    },
    toFullUrl(url) {
      if (!url) return ''
      if (/^https?:\/\//.test(url)) return url
      return `${API_CONFIG.baseURL.replace(/\/api$/, '')}${url}`
    },
    fileNameFromPath(filePath) {
      const name = String(filePath || '').split('/').pop() || ''
      return name.split('?')[0] || '图片'
    },
    async runReportScan(filePath) {
      uni.showLoading({ title: '识别中' })
      try {
        const result = await scanReport(filePath, { source_type: this.sourceType })
        this.applyScanResult(result)
        uni.showToast({ title: '识别完成', icon: 'success' })
      } catch (error) {
        uni.showToast({ title: (error && error.message) || '识别失败', icon: 'none' })
      } finally {
        uni.hideLoading()
      }
    },
    async submitReport() {
      if (this.isSubmitting) return
      const name = this.form.name.trim()
      if (!name) {
        uni.showToast({ title: '请填写报告名称', icon: 'none' })
        return
      }
      if (!this.images.length) {
        uni.showToast({ title: '请至少上传一张图片', icon: 'none' })
        return
      }
      if ([...this.images, ...this.files].some((item) => item.uploading)) {
        uni.showToast({ title: '附件正在上传，请稍候', icon: 'none' })
        return
      }
      this.isSubmitting = true
      uni.showLoading({ title: '提交中' })
      try {
        await submitReportApi({
          name,
          category: this.categories[this.categoryIndex],
          entryTime: `${this.form.entryDate} ${this.form.entryTime}`,
          reportTime: `${this.form.reportDate} ${this.form.reportTime}`,
          images: this.images.map((item) => ({ name: this.fileNameFromPath(item.preview), url: item.url })),
          files: this.files.map((item) => ({ name: item.name, url: item.url, size: item.size })),
          ocr: {
            fields: this.rawFields,
            texts: this.rawTexts,
            storedFile: this.storedFile,
            outputDir: this.outputDir
          }
        })
        uni.showToast({ title: '上传成功', icon: 'success' })
        setTimeout(() => uni.navigateBack(), 600)
      } catch (error) {
        uni.showToast({ title: (error && error.message) || '提交失败', icon: 'none' })
      } finally {
        this.isSubmitting = false
        uni.hideLoading()
      }
    },
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
      this.outputDir = result.outputDir || ''
      this.leafletCandidate = result.leafletCandidate || null
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
        const title = this.sourceType === 'medicine' ? '药品信息确认' : '体检报告确认'
        await confirmOcrResult({
          sourceType: this.sourceType,
          title,
          fields: this.rawFields,
          texts: this.rawTexts,
          storedFile: this.storedFile,
          outputDir: this.outputDir,
          leafletCandidate: this.leafletCandidate
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
.page-content.with-action-bar { padding-bottom: 190rpx; }
.page-desc { display: block; font-size: 26rpx; color: #71817A; line-height: 1.6; }

.form-card, .scan-card, .result-card { margin-top: 28rpx; padding: 30rpx; border-radius: 22rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 10rpx 24rpx rgba(31, 72, 55, 0.05); }
.form-card .section-title { display: block; }
.section-head { display: flex; justify-content: space-between; align-items: center; gap: 20rpx; }
.section-title { font-size: 30rpx; color: #17231F; font-weight: 700; }
.section-tip { color: #9AA8A1; font-size: 22rpx; }
.form-row { display: flex; align-items: center; justify-content: space-between; min-height: 88rpx; border-bottom: 1rpx solid #EEF4F1; }
.form-row:last-child { border-bottom: none; }
.form-label { color: #50605A; font-size: 27rpx; flex-shrink: 0; }
.form-input { flex: 1; height: 88rpx; margin-left: 24rpx; text-align: right; font-size: 27rpx; color: #17231F; }
.form-placeholder { color: #A8B4AE; }
.form-value-wrap { display: flex; align-items: center; gap: 8rpx; }
.form-value { font-size: 34rpx; color: #17231F; font-weight: 600; }
.form-arrow { color: #A8B4AE; font-size: 32rpx; line-height: 1; }
.datetime-row { display: flex; align-items: center; gap: 12rpx; }
.datetime-pill { padding: 14rpx 24rpx; border-radius: 12rpx; background: #F0FAF6; color: #0E7F72; font-size: 34rpx; font-weight: 600; }

.picker-mask { position: fixed; left: 0; right: 0; top: 0; bottom: 0; z-index: 1200; background: rgba(23, 35, 31, 0.45); display: flex; align-items: flex-end; }
.picker-sheet { width: 100%; background: #FFFFFF; border-radius: 28rpx 28rpx 0 0; padding-bottom: calc(20rpx + env(safe-area-inset-bottom)); animation: sheet-up 0.22s ease-out; }
.picker-header { display: flex; align-items: center; justify-content: space-between; padding: 26rpx 32rpx; border-bottom: 1rpx solid #EEF4F1; }
.picker-title { font-size: 32rpx; font-weight: 700; color: #17231F; }
.picker-cancel { font-size: 30rpx; color: #71817A; padding: 6rpx 12rpx; }
.picker-confirm { font-size: 30rpx; color: #0E9F8E; font-weight: 700; padding: 6rpx 12rpx; }
.picker-columns { display: flex; height: 460rpx; }
.wheel-column-wrap { flex: 1; height: 100%; overflow: hidden; }
.wheel-column { width: 100%; height: 460rpx; }
.wheel-pad { height: 184rpx; }
.wheel-item { height: 92rpx; line-height: 92rpx; text-align: center; font-size: 38rpx; color: #8A9992; }
.wheel-item.active { color: #0E9F8E; font-weight: 700; font-size: 42rpx; }
@keyframes sheet-up { from { transform: translateY(100%); } to { transform: translateY(0); } }

.pick-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20rpx; margin-top: 24rpx; }
.pick-block { height: 180rpx; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16rpx; border-radius: 16rpx; background: #F7FBF9; border: 1rpx dashed #BFDCD2; }
.pick-block-hover { background: #EAF6F1; }
.pick-label { color: #0E7F72; font-size: 26rpx; font-weight: 600; }

.anim-icon { position: relative; width: 96rpx; height: 96rpx; }
.cam { animation: float 2.4s ease-in-out infinite; }
.cam-body { position: absolute; left: 6rpx; right: 6rpx; top: 26rpx; bottom: 12rpx; border-radius: 14rpx; background: #0E9F8E; }
.cam-top { position: absolute; left: 26rpx; top: -12rpx; width: 34rpx; height: 14rpx; border-radius: 6rpx 6rpx 0 0; background: #0E9F8E; }
.cam-lens { position: absolute; left: 50%; top: 50%; width: 34rpx; height: 34rpx; margin: -17rpx 0 0 -17rpx; border-radius: 50%; background: #F0FAF6; border: 6rpx solid #0B8478; box-sizing: border-box; animation: lens 2.4s ease-in-out infinite; }
.cam-flash { position: absolute; right: 14rpx; top: 10rpx; width: 12rpx; height: 12rpx; border-radius: 50%; background: #FDE68A; animation: blink 1.6s ease-in-out infinite; }

.photo { animation: tilt 3s ease-in-out infinite; }
.photo-frame { position: absolute; left: 12rpx; right: 12rpx; top: 16rpx; bottom: 16rpx; border-radius: 12rpx; background: #0E9F8E; overflow: hidden; }
.photo-sun { position: absolute; left: 16rpx; top: 14rpx; width: 18rpx; height: 18rpx; border-radius: 50%; background: #FDE68A; animation: blink 2s ease-in-out infinite; }
.photo-hill { position: absolute; left: 12rpx; bottom: 10rpx; width: 0; height: 0; border-left: 24rpx solid transparent; border-right: 24rpx solid transparent; border-bottom: 28rpx solid #F0FAF6; }
.photo-hill.second { left: 48rpx; bottom: 10rpx; border-left-width: 18rpx; border-right-width: 18rpx; border-bottom-width: 22rpx; }

@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8rpx); } }
@keyframes lens { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.12); } }
@keyframes blink { 0%, 100% { opacity: 0.35; } 50% { opacity: 1; } }
@keyframes tilt { 0%, 100% { transform: rotate(-4deg); } 50% { transform: rotate(4deg); } }

.image-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx; margin-top: 24rpx; }
.image-item { position: relative; width: 100%; height: 180rpx; border-radius: 14rpx; overflow: hidden; background: #F4F7F5; }
.image-thumb { width: 100%; height: 100%; }
.image-mask { position: absolute; left: 0; right: 0; top: 0; bottom: 0; display: flex; align-items: center; justify-content: center; background: rgba(23, 35, 31, 0.45); }
.image-mask-text { color: #FFFFFF; font-size: 22rpx; }
.image-remove { position: absolute; right: 8rpx; top: 8rpx; width: 40rpx; height: 40rpx; border-radius: 50%; background: rgba(23, 35, 31, 0.6); color: #FFFFFF; font-size: 28rpx; line-height: 38rpx; text-align: center; }

.add-file-btn { padding: 8rpx 18rpx; border-radius: 999rpx; background: #E1F3ED; color: #0E7F72; font-size: 24rpx; font-weight: 600; }
.file-list { margin-top: 16rpx; }
.file-item { display: flex; align-items: center; justify-content: space-between; padding: 22rpx 0; border-bottom: 1rpx solid #EEF4F1; }
.file-item:last-child { border-bottom: none; }
.file-main { flex: 1; min-width: 0; }
.file-name { display: block; color: #17231F; font-size: 26rpx; font-weight: 600; word-break: break-all; }
.file-meta { display: block; margin-top: 6rpx; color: #9AA8A1; font-size: 22rpx; }
.file-delete { flex-shrink: 0; margin-left: 20rpx; color: #B91C1C; font-size: 24rpx; }
.empty-tip { display: block; margin-top: 20rpx; color: #A8B4AE; font-size: 24rpx; }


.scan-frame { position: relative; width: 100%; height: 280rpx; border-radius: 16rpx; background: #F0FAF6; display: flex; align-items: center; justify-content: center; }
.scan-image { width: 88rpx; height: 88rpx; opacity: 0.6; }.corner { position: absolute; width: 46rpx; height: 46rpx; border-color: #0E9F8E; border-style: solid; }.top-left { left: 26rpx; top: 26rpx; border-width: 6rpx 0 0 6rpx; }.top-right { right: 26rpx; top: 26rpx; border-width: 6rpx 6rpx 0 0; }.bottom-left { left: 26rpx; bottom: 26rpx; border-width: 0 0 6rpx 6rpx; }.bottom-right { right: 26rpx; bottom: 26rpx; border-width: 0 6rpx 6rpx 0; }
.scan-title { display: block; margin-top: 28rpx; font-size: 32rpx; color: #17231F; font-weight: 700; }.scan-desc { display: block; margin-top: 12rpx; font-size: 25rpx; color: #71817A; line-height: 1.55; }
.scan-actions { display: grid; gap: 16rpx; margin-top: 28rpx; }.scan-btn, .save-btn { height: 84rpx; display: flex; align-items: center; justify-content: center; border-radius: 14rpx; background: #F4F7F5; color: #50605A; font-size: 28rpx; font-weight: 600; border: 1rpx solid #DDE7E1; }.scan-btn.primary, .save-btn { background: #0E9F8E; color: #FFFFFF; border-color: #0E9F8E; font-weight: 700; }

.confidence { padding: 8rpx 14rpx; border-radius: 999rpx; background: #E1F3ED; color: #0E9F8E; font-size: 22rpx; font-weight: 700; }
.result-meta { display: flex; justify-content: space-between; align-items: center; margin-top: 24rpx; padding-bottom: 20rpx; border-bottom: 1rpx solid #E8F1ED; }.result-meta-label { color: #71817A; font-size: 25rpx; }.result-meta-value { color: #17231F; font-size: 25rpx; font-weight: 700; }
.table-scroll { width: 100%; margin-top: 12rpx; }
.ocr-table { min-width: 1080rpx; }
.ocr-table.medicine { min-width: 860rpx; }.medicine-name { width: 300rpx; color: #17231F; }.medicine-value { width: 430rpx; color: #17231F; }.medicine-status { width: 130rpx; text-align: center; color: #187A83; font-weight: 600; }.medicine-table-head .table-cell { color: #187A83; }.medicine-table-row { min-height: 92rpx; }
.table-row { display: flex; align-items: center; min-height: 82rpx; border-bottom: 1rpx solid #E8F1ED; }.table-row.warning { background: #FFF9F1; }.table-head { min-height: 68rpx; background: #F0FAF6; border-radius: 10rpx; border-bottom: none; }.table-cell { flex-shrink: 0; padding: 18rpx 14rpx; box-sizing: border-box; color: #50605A; font-size: 23rpx; line-height: 1.35; word-break: break-all; }.table-cell.name { width: 360rpx; color: #17231F; }.table-cell.value { width: 170rpx; font-weight: 700; color: #17231F; }.table-cell.unit { width: 160rpx; }.table-cell.reference { width: 230rpx; }.table-cell.status { width: 140rpx; text-align: center; color: #36B37E; font-weight: 600; }.table-head .table-cell { padding-top: 14rpx; padding-bottom: 14rpx; color: #0E9F8E; font-size: 22rpx; font-weight: 700; }.table-row.warning .table-cell.value, .table-cell.status.warning { color: #C56F20; }.table-cell.status.pending { color: #9A7A3A; }
.notice-box { margin-top: 22rpx; padding: 24rpx; border-radius: 14rpx; background: #FFF7ED; color: #B96B25; font-size: 24rpx; line-height: 1.5; border: 1rpx solid #F3D8B7; }
.leaflet-source { display: block; margin-top: 16rpx; color: #71817A; font-size: 23rpx; }
.leaflet-section { margin-top: 22rpx; padding-top: 20rpx; border-top: 1rpx solid #E8F1ED; }
.leaflet-section-title { display: block; color: #0E7F72; font-size: 27rpx; font-weight: 700; }
.leaflet-section-content { display: block; margin-top: 10rpx; color: #50605A; font-size: 25rpx; line-height: 1.6; white-space: pre-wrap; }
.leaflet-notice { margin-top: 22rpx; }.confidence.blocked { background: #FFF7ED; color: #B96B25; }
.result-action-bar { position: fixed; left: 0; right: 0; bottom: 0; z-index: 998; display: flex; gap: 16rpx; padding: 18rpx 32rpx calc(18rpx + env(safe-area-inset-bottom)); background: rgba(255, 255, 255, 0.96); border-top: 1rpx solid #DDE7E1; box-shadow: 0 -8rpx 24rpx rgba(31, 72, 55, 0.08); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); }
.action-btn { flex: 1; height: 84rpx; display: flex; align-items: center; justify-content: center; border-radius: 14rpx; font-size: 28rpx; font-weight: 700; }.action-btn.secondary { color: #50605A; background: #F4F7F5; border: 1rpx solid #DDE7E1; }.action-btn.primary { color: #FFFFFF; background: #0E9F8E; border: 1rpx solid #0E9F8E; }
</style>

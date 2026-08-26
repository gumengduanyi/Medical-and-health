<template>
  <view class="container">
    <view class="header">
      <view><text class="title">个人健康信息</text><text class="desc">AI 建议会结合这些基础信息、病史和药物过敏史生成。</text></view>
      <button class="top-edit-btn" @click="toggleEdit">{{ isEdit ? '取消' : '修改' }}</button>
    </view>

    <view class="summary-card">
      <view class="summary-item"><text class="summary-value">22.9</text><text class="summary-label">BMI</text></view>
      <view class="summary-item"><text class="summary-value">高血压</text><text class="summary-label">重点病史</text></view>
      <view class="summary-item"><text class="summary-value">无</text><text class="summary-label">药物过敏</text></view>
    </view>

    <view class="status-card">
      <text class="status-title">健康画像完成度 {{ completion }}%</text>
      <text class="status-desc">建议至少补全姓名、年龄、身高体重、过敏史和既往病史。</text>
      <view class="status-bar"><view class="status-fill" :style="{ width: completion + '%' }"></view></view>
    </view>

    <view class="form-card">
      <view class="form-item" v-for="item in fields" :key="item.key">
        <text class="label">{{ item.label }}<text v-if="item.required" class="required">*</text></text>
        <input class="input" v-model="formData[item.key]" :placeholder="item.placeholder" :disabled="!isEdit" />
      </view>
    </view>

    <view class="notice-card"><text class="notice-title">AI 个性化依据</text><text class="notice-text">完善过敏史、既往病史和家族史后，AI 可以更准确地判断药品禁忌、指标异常风险和复诊建议。</text></view>

    <view class="save-wrap" v-if="isEdit"><button class="save-btn" @click="saveInfo">保存信息</button></view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      isEdit: false,
      fields: [
        { key: 'name', label: '姓名', placeholder: '请输入姓名', required: true }, { key: 'sex', label: '性别', placeholder: '请输入性别' }, { key: 'age', label: '年龄', placeholder: '请输入年龄', required: true }, { key: 'height', label: '身高(cm)', placeholder: '请输入身高', required: true }, { key: 'weight', label: '体重(kg)', placeholder: '请输入体重', required: true }, { key: 'allergy', label: '药物过敏史', placeholder: '如：青霉素过敏', required: true }, { key: 'disease', label: '既往病史', placeholder: '如：高血压、糖尿病', required: true }, { key: 'familyHistory', label: '家族史', placeholder: '请填写家族史' }, { key: 'geneticHistory', label: '遗传病史', placeholder: '请填写遗传病史' }, { key: 'disableInfo', label: '残疾情况', placeholder: '请填写残疾情况' }
      ],
      formData: { name: '王先生', sex: '男', age: '60', height: '172', weight: '68', allergy: '无', disease: '高血压', familyHistory: '无', geneticHistory: '无', disableInfo: '无' }
    }
  },
  computed: {
    completion() {
      const keys = ['name', 'age', 'height', 'weight', 'allergy', 'disease', 'familyHistory']
      const filled = keys.filter((key) => this.formData[key]).length
      return Math.round(filled / keys.length * 100)
    }
  },
  methods: {
    toggleEdit() { this.isEdit = !this.isEdit },
    saveInfo() {
      if (!this.formData.name || !this.formData.age) {
        uni.showToast({ title: '请补全姓名和年龄', icon: 'none' })
        return
      }
      uni.showToast({ title: '保存成功', icon: 'success' }); this.isEdit = false
    }
  }
}
</script>

<style scoped>
.container { min-height: 100vh; background: linear-gradient(180deg, #EEFBF7 0%, #F8FAFC 34%, #F8FAFC 100%); padding: 28rpx 28rpx 120rpx; box-sizing: border-box; }.header { display: flex; align-items: flex-start; justify-content: space-between; gap: 20rpx; padding: 12rpx 0 26rpx; }.title { display: block; font-size: 40rpx; font-weight: 900; color: #1E293B; }.desc { display: block; max-width: 490rpx; margin-top: 10rpx; font-size: 24rpx; line-height: 1.45; color: #64748B; }
.top-edit-btn { margin: 0; min-width: 118rpx; height: 66rpx; line-height: 66rpx; background: #0F766E; color: #fff; border: none; border-radius: 14rpx; font-size: 27rpx; font-weight: 800; }
.summary-card { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx; margin-bottom: 24rpx; }.summary-item { padding: 24rpx 12rpx; text-align: center; border-radius: 16rpx; background: #fff; box-shadow: 0 8rpx 22rpx rgba(15,23,42,.05); }.summary-value { display: block; font-size: 30rpx; color: #0F766E; font-weight: 900; }.summary-label { display: block; margin-top: 8rpx; font-size: 22rpx; color: #64748B; }
.status-card { margin-bottom: 24rpx; padding: 28rpx; border-radius: 16rpx; background: linear-gradient(135deg, #ECFDF5, #EFF6FF); border: 1rpx solid #BFDBFE; }
.status-title { display: block; font-size: 30rpx; color: #0F766E; font-weight: 900; }.status-desc { display: block; margin-top: 10rpx; font-size: 24rpx; color: #334155; line-height: 1.5; }.status-bar { height: 12rpx; margin-top: 20rpx; border-radius: 999rpx; background: rgba(255,255,255,.8); overflow: hidden; }.status-fill { height: 100%; border-radius: 999rpx; background: linear-gradient(90deg, #10B981, #2563EB); }
.form-card, .notice-card { background: #fff; border-radius: 16rpx; padding: 30rpx; box-shadow: 0 8rpx 22rpx rgba(15,23,42,.05); }.form-item { display: flex; align-items: center; padding: 24rpx 0; border-bottom: 1rpx solid #F1F5F9; }.form-item:last-child { border-bottom: none; }.label { width: 180rpx; font-size: 26rpx; color: #64748B; }.input { flex: 1; font-size: 28rpx; color: #1E293B; }.input[disabled] { color: #334155; }
.required { color: #E11D48; margin-left: 4rpx; }
.notice-card { margin-top: 24rpx; background: linear-gradient(180deg, #FFFFFF, #ECFDF5); }.notice-title { display: block; font-size: 30rpx; color: #0F766E; font-weight: 900; }.notice-text { display: block; margin-top: 12rpx; font-size: 25rpx; color: #334155; line-height: 1.6; }.save-wrap { margin-top: 36rpx; }.save-btn { width: 100%; height: 86rpx; line-height: 86rpx; background: #0F766E; color: #fff; border: none; border-radius: 14rpx; font-size: 30rpx; font-weight: 800; }
</style>

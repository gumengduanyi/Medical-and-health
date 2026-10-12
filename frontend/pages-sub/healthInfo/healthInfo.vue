<template>
  <view class="container">
    <view class="custom-nav">
      <view class="status-bar"></view>
      <view class="nav-content">
        <view class="nav-back" @click="goBack">
          <text class="nav-back-icon">‹</text>
        </view>
        <text class="nav-title">个人健康信息</text>
        <view class="top-edit-btn" @click="toggleEdit">{{ isEdit ? '保存' : '修改' }}</view>
      </view>
    </view>

    <view class="page-content">
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
    </view>
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
    goBack() { uni.navigateBack() },
    toggleEdit() {
      if (this.isEdit) {
        this.saveInfo()
      } else {
        this.isEdit = true
      }
    },
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
.container { min-height: 100vh; background: #F4F7F5; }
.custom-nav { position: fixed; top: 0; left: 0; right: 0; z-index: 999; background: rgba(244, 247, 245, 0.92); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-bottom: 1rpx solid #DDE7E1; }
.status-bar { height: var(--status-bar-height); }
.nav-content { height: 100rpx; padding: 0 32rpx; display: flex; align-items: center; justify-content: space-between; position: relative; }
.nav-back { width: 60rpx; height: 60rpx; display: flex; align-items: center; justify-content: center; }
.nav-back-icon { font-size: 56rpx; color: #17231F; font-weight: 300; line-height: 1; }
.nav-title { position: absolute; left: 50%; transform: translateX(-50%); font-size: 36rpx; font-weight: 700; color: #17231F; }
.top-edit-btn { padding: 12rpx 24rpx; background: #E1F3ED; color: #0E9F8E; border-radius: 8rpx; font-size: 26rpx; font-weight: 600; border: 1rpx solid #BFE3D6; }
.page-content { padding: 32rpx; padding-top: calc(var(--status-bar-height) + 100rpx + 32rpx); padding-bottom: 80rpx; }

.summary-card { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx; }.summary-item { padding: 28rpx 12rpx; text-align: center; border-radius: 18rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; }.summary-value { display: block; font-size: 32rpx; color: #0E9F8E; font-weight: 700; }.summary-label { display: block; margin-top: 10rpx; font-size: 22rpx; color: #71817A; }
.status-card { margin-top: 24rpx; padding: 32rpx; border-radius: 22rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 10rpx 24rpx rgba(31, 72, 55, 0.05); }
.status-title { display: block; font-size: 30rpx; color: #17231F; font-weight: 700; }.status-desc { display: block; margin-top: 10rpx; font-size: 24rpx; color: #71817A; line-height: 1.5; }.status-bar { height: 12rpx; margin-top: 20rpx; border-radius: 999rpx; background: #E8F1ED; overflow: hidden; }.status-fill { height: 100%; border-radius: 999rpx; background: #0E9F8E; }
.form-card { margin-top: 24rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; border-radius: 22rpx; padding: 32rpx; box-shadow: 0 10rpx 24rpx rgba(31, 72, 55, 0.05); }.form-item { display: flex; align-items: center; padding: 24rpx 0; border-bottom: 1rpx solid #E8F1ED; }.form-item:last-child { border-bottom: none; }.label { width: 180rpx; font-size: 26rpx; color: #71817A; }.input { flex: 1; font-size: 28rpx; color: #17231F; }.input[disabled] { color: #50605A; }
.required { color: #E58A3A; margin-left: 4rpx; }
</style>

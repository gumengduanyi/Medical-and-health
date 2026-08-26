<template>
  <view class="page-container">
    <view class="header-card">
      <view>
        <text class="page-title">AI 健康问答</text>
        <text class="page-desc">基于报告、药箱和健康档案，回答指标含义、用药注意和复诊建议。</text>
      </view>
      <view class="header-icon-wrap"><image class="header-icon" src="/static/icons/sparkle.png" mode="aspectFit" /></view>
    </view>

    <view class="chat-card">
      <view class="chat-item assistant">
        <view class="avatar">AI</view>
        <view class="bubble">
          <text class="bubble-text">{{ assistantReply }}</text>
          <text v-if="safetyNotice" class="safety-note">{{ safetyNotice }}</text>
        </view>
      </view>
      <view class="question-chips">
        <text class="chip" v-for="item in questions" :key="item" @click="ask(item)">{{ item }}</text>
      </view>
      <view class="chat-item user" v-if="currentQuestion">
        <view class="bubble user-bubble">
          <text class="bubble-text">{{ currentQuestion }}</text>
        </view>
        <view class="avatar user-avatar">我</view>
      </view>
      <view class="chat-item assistant" v-if="currentQuestion">
        <view class="avatar">AI</view>
        <view class="bubble">
          <text class="bubble-text">{{ loading ? '正在检索资料...' : assistantReply }}</text>
          <view v-if="sourceList.length" class="source-list">
            <view class="source-item" v-for="source in sourceList" :key="source.id">
              <text class="source-title">{{ source.title }}</text>
              <text class="source-excerpt">{{ source.excerpt }}</text>
            </view>
          </view>
          <text v-if="safetyNotice" class="safety-note">{{ safetyNotice }}</text>
        </view>
      </view>
    </view>

    <view class="chat-input-row">
      <input class="chat-input" v-model="inputText" placeholder="输入你想问的问题" />
      <button class="send-btn" :disabled="loading" @click="ask(inputText)">{{ loading ? '...' : '发送' }}</button>
    </view>
  </view>
</template>

<script>
import { sendAiMessage } from '@/services/modules/ai.service.js'

export default {
  data() {
    return {
      inputText: '',
      currentQuestion: '',
      assistantReply: '你好，我可以帮你检索你的健康档案、报告和药品记录，并给出带来源的解释。',
      sourceList: [],
      safetyNotice: '回答仅供健康资料整理与风险提示，不替代医生诊断。',
      loading: false,
      questions: ['我的血压为什么偏高？', '这份体检报告要注意什么？', '阿司匹林有什么禁忌？', '我今天该先处理什么？']
    }
  },
  methods: {
    async ask(text) {
      if (!text) return
      this.currentQuestion = text
      this.inputText = ''
      this.loading = true
      try {
        const response = await sendAiMessage({
          message: text,
          context: { profile_id: 'profile_001' }
        })
        this.assistantReply = response.content || '当前资料不足，暂时没有可返回的结论。'
        this.sourceList = response.sources || []
        this.safetyNotice = response.safety_notice || ''
      } catch (error) {
        this.assistantReply = '暂时无法获取检索结果，请稍后重试。'
        this.sourceList = []
        this.safetyNotice = '系统当前未能完成检索。'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.page-container { min-height: 100vh; padding: 28rpx 28rpx 150rpx; background: linear-gradient(180deg, #EEF2FF 0%, #F8FAFC 34%, #F8FAFC 100%); box-sizing: border-box; }
.header-card { display: flex; justify-content: space-between; align-items: center; gap: 20rpx; padding: 36rpx; border-radius: 18rpx; color: #fff; background: linear-gradient(135deg, #2563EB, #0F766E); box-shadow: 0 16rpx 36rpx rgba(37,99,235,.18); }
.page-title { display: block; font-size: 40rpx; font-weight: 900; }.page-desc { display: block; margin-top: 10rpx; font-size: 24rpx; line-height: 1.5; opacity: .9; }.header-icon-wrap { width: 86rpx; height: 86rpx; border-radius: 16rpx; background: rgba(255,255,255,.18); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }.header-icon { width: 48rpx; height: 48rpx; }
.chat-card { margin-top: 24rpx; padding: 30rpx; border-radius: 16rpx; background: #fff; box-shadow: 0 8rpx 22rpx rgba(15,23,42,.05); }
.chat-item { display: flex; gap: 16rpx; margin-bottom: 24rpx; }.chat-item.user { justify-content: flex-end; }.avatar { width: 64rpx; height: 64rpx; border-radius: 50%; background: #D1FAE5; color: #059669; display: flex; align-items: center; justify-content: center; font-size: 22rpx; font-weight: 900; flex-shrink: 0; }.user-avatar { background: #DBEAFE; color: #2563EB; }
.bubble { max-width: 520rpx; padding: 20rpx 24rpx; border-radius: 16rpx; background: #F1F5F9; color: #1E293B; font-size: 27rpx; line-height: 1.55; }.user-bubble { background: #D1FAE5; }
.bubble-text { display: block; }
.source-list { margin-top: 16rpx; display: grid; gap: 12rpx; }
.source-item { padding: 14rpx 16rpx; border-radius: 14rpx; background: #FFFFFF; border: 1rpx solid #E2E8F0; }
.source-title { display: block; font-size: 23rpx; font-weight: 800; color: #0F766E; }
.source-excerpt { display: block; margin-top: 6rpx; font-size: 21rpx; line-height: 1.45; color: #475569; }
.safety-note { display: block; margin-top: 12rpx; font-size: 21rpx; line-height: 1.4; color: #64748B; }
.question-chips { display: flex; flex-wrap: wrap; gap: 14rpx; margin: 18rpx 0 28rpx; }.chip { padding: 12rpx 18rpx; border-radius: 999rpx; background: #ECFDF5; color: #059669; font-size: 24rpx; }
.chat-input-row { position: fixed; left: 0; right: 0; bottom: 0; display: flex; gap: 14rpx; padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom)); background: rgba(255,255,255,.96); border-top: 1rpx solid #E2E8F0; }.chat-input { flex: 1; height: 76rpx; padding: 0 22rpx; border-radius: 14rpx; background: #F1F5F9; font-size: 27rpx; }.send-btn { width: 120rpx; height: 76rpx; line-height: 76rpx; border-radius: 14rpx; background: #0F766E; color: #fff; font-size: 26rpx; border: none; }.send-btn[disabled] { opacity: 0.65; }
</style>

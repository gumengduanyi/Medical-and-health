<template>
  <view class="page-container">
    <view class="custom-nav">
      <view class="status-bar"></view>
      <view class="nav-content">
        <view class="nav-back" @click="goBack"><text class="nav-back-icon">‹</text></view>
        <text class="nav-title">AI 健康问答</text>
        <view class="nav-placeholder"></view>
      </view>
    </view>

    <view class="page-content">
    <view class="chat-card">
      <view v-for="item in messages" :key="item.id" class="chat-item" :class="item.role">
        <view v-if="item.role === 'assistant'" class="avatar">AI</view>
        <view class="bubble" :class="{ 'user-bubble': item.role === 'user' }">
          <text class="bubble-text">{{ item.content }}</text>
          <view v-if="item.sources && item.sources.length" class="source-list">
            <view class="source-item" v-for="(source, index) in item.sources" :key="`${source.id}-${index}`">
              <text class="source-title">{{ source.title }}</text>
              <text class="source-excerpt">{{ source.excerpt }}</text>
            </view>
          </view>
          <text v-if="item.safetyNotice" class="safety-note">{{ item.safetyNotice }}</text>
          <text v-if="item.retryMessage" class="retry-message" @click="retry(item.retryMessage)">{{ item.retryMessage }}</text>
        </view>
        <view v-if="item.role === 'user'" class="avatar user-avatar">我</view>
      </view>
      <view class="question-chips">
        <text class="chip" v-for="item in questions" :key="item" @click="ask(item)">{{ item }}</text>
      </view>
    </view>

    </view>

    <view class="chat-input-row">
      <input class="chat-input" v-model="inputText" placeholder="输入你想问的问题" confirm-type="send" @confirm="ask(inputText)" />
      <view class="send-btn" :class="{ disabled: loading }" @click="ask(inputText)">{{ loading ? '...' : '发送' }}</view>
    </view>
  </view>
</template>

<script>
import { sendAiMessage } from '@/services/modules/ai.service.js'

export default {
  data() {
    return {
      inputText: '',
      nextMessageId: 2,
      messages: [{
        id: 1,
        role: 'assistant',
        content: '你好，我可以帮你检索你的健康档案、报告和药品记录，并给出带来源的解释。',
        sources: [],
        safetyNotice: '回答仅供健康资料整理与风险提示，不替代医生诊断。'
      }],
      loading: false,
      questions: ['我的血压为什么偏高？', '这份体检报告要注意什么？', '阿司匹林有什么禁忌？', '我今天该先处理什么？']
    }
  },
  methods: {
    goBack() { uni.navigateBack() },
    async ask(text) {
      const message = String(text || '').trim()
      if (!message || this.loading) return

      this.inputText = ''
      this.messages.push({ id: this.nextMessageId++, role: 'user', content: message })
      const assistantId = this.nextMessageId++
      this.messages.push({
        id: assistantId,
        role: 'assistant',
        content: '正在检索资料...',
        sources: [],
        safetyNotice: ''
      })
      this.loading = true
      try {
        const response = await sendAiMessage({
          message,
          context: { profile_id: 'profile_001' }
        })
        this.updateAssistantMessage(assistantId, {
          content: response.content || '当前资料不足，暂时没有可返回的结论。',
          sources: response.sources || [],
          safetyNotice: response.safety_notice || ''
        })
      } catch (error) {
        const errorMessage = error && error.message ? error.message : '请确认手机与电脑连接同一网络，并检查后端服务是否运行。'
        this.updateAssistantMessage(assistantId, {
          content: `暂时无法获取检索结果：${errorMessage}`,
          sources: [],
          safetyNotice: '请检查网络连接和后端服务。',
          retryMessage: message
        })
      } finally {
        this.loading = false
      }
    },
    retry(message) {
      if (!this.loading) this.ask(message)
    },
    updateAssistantMessage(id, updates) {
      const index = this.messages.findIndex(item => item.id === id)
      if (index < 0) return
      this.messages[index] = { ...this.messages[index], ...updates }
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
.page-content { padding: 32rpx; padding-top: calc(var(--status-bar-height) + 100rpx + 32rpx); padding-bottom: 150rpx; }

.chat-card { padding: 32rpx; border-radius: 22rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; box-shadow: 0 10rpx 24rpx rgba(31, 72, 55, 0.05); }
.chat-item { display: flex; gap: 16rpx; margin-bottom: 24rpx; }.chat-item.user { justify-content: flex-end; }.avatar { width: 64rpx; height: 64rpx; border-radius: 50%; background: #E1F3ED; color: #0E9F8E; display: flex; align-items: center; justify-content: center; font-size: 22rpx; font-weight: 700; flex-shrink: 0; }.user-avatar { background: #EEF2F0; color: #50605A; }
.bubble { max-width: 520rpx; padding: 20rpx 24rpx; border-radius: 16rpx; background: #F0F4F1; color: #17231F; font-size: 27rpx; line-height: 1.55; }.user-bubble { background: #E1F3ED; }
.bubble-text { display: block; }
.source-list { margin-top: 16rpx; display: grid; gap: 12rpx; }
.source-item { padding: 16rpx 18rpx; border-radius: 14rpx; background: #F4F7F5; border: 1rpx solid #DDE7E1; }
.source-title { display: block; font-size: 23rpx; font-weight: 700; color: #0E9F8E; }
.source-excerpt { display: block; margin-top: 8rpx; font-size: 21rpx; line-height: 1.45; color: #71817A; }
.safety-note { display: block; margin-top: 12rpx; font-size: 21rpx; line-height: 1.4; color: #9AA8A1; }
.question-chips { display: flex; flex-wrap: wrap; gap: 14rpx; margin: 18rpx 0 28rpx; }.chip { padding: 12rpx 20rpx; border-radius: 999rpx; background: #E1F3ED; color: #0E9F8E; font-size: 24rpx; border: 1rpx solid #BFE3D6; }
.chat-input-row { position: fixed; left: 0; right: 0; bottom: 0; display: flex; gap: 14rpx; padding: 18rpx 28rpx calc(18rpx + env(safe-area-inset-bottom)); background: rgba(244, 247, 245, 0.96); border-top: 1rpx solid #DDE7E1; }.chat-input { flex: 1; height: 76rpx; padding: 0 22rpx; border-radius: 14rpx; background: #FFFFFF; border: 1rpx solid #DDE7E1; color: #17231F; font-size: 27rpx; }.send-btn { width: 120rpx; height: 76rpx; display: flex; align-items: center; justify-content: center; border-radius: 14rpx; background: #0E9F8E; color: #FFFFFF; font-size: 26rpx; font-weight: 700; }.send-btn.disabled { opacity: 0.5; }
</style>

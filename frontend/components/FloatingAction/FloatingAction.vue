<template>
  <view
    class="fab-view"
    :style="fabStyle"
    @touchstart.stop="onTouchStart"
    @touchmove.stop.prevent="onTouchMove"
    @touchend.stop="onTouchEnd"
    @tap.stop="handleTap"
  >
    <view class="fab-core">
      <view class="fab-glow"></view>
      <text class="fab-main">AI</text>
      <text class="fab-sub">OCR</text>
    </view>
  </view>
</template>

<script>
import { smoothNavigateTo } from '@/utils/router.js'

export default {
  name: 'FloatingAction',
  props: {
    url: {
      type: String,
      default: '/pages-sub/ai_chat/ai_chat'
    }
  },
  data() {
    return {
      x: 300,
      y: 520,
      startX: 0,
      startY: 0,
      dragOffsetX: 0,
      dragOffsetY: 0,
      startTime: 0,
      buttonSize: 58,
      windowWidth: 375,
      windowHeight: 667,
      moved: false,
      pendingX: null,
      pendingY: null,
      dragFrame: null
    }
  },
  computed: {
    fabStyle() {
      return `transform: translate3d(${this.x}px, ${this.y}px, 0);`
    }
  },
  mounted() {
    this.initPosition()
  },
  methods: {
    clamp(value, min, max) {
      return Math.min(Math.max(value, min), max)
    },
    refreshSystemInfo() {
      const info = uni.getSystemInfoSync()
      this.windowWidth = info.windowWidth || this.windowWidth
      this.windowHeight = info.windowHeight || this.windowHeight
      this.buttonSize = Math.max(54, Math.round(116 * this.windowWidth / 750))
    },
    initPosition() {
      try {
        this.refreshSystemInfo()
        const saved = uni.getStorageSync('floating_action_position')
        const maxX = this.windowWidth - this.buttonSize - 6
        const maxY = this.windowHeight - this.buttonSize - 6
        if (saved && typeof saved.x === 'number' && typeof saved.y === 'number') {
          this.x = this.clamp(saved.x, 6, maxX)
          this.y = this.clamp(saved.y, 24, maxY)
          return
        }
        this.x = maxX - 10
        this.y = maxY - 88
      } catch (e) {
        this.x = 300
        this.y = 520
      }
    },
    onTouchStart(event) {
      const touch = event.changedTouches && event.changedTouches[0]
      if (!touch) return
      try { this.refreshSystemInfo() } catch (e) {}
      this.startX = touch.clientX
      this.startY = touch.clientY
      this.dragOffsetX = touch.clientX - this.x
      this.dragOffsetY = touch.clientY - this.y
      this.startTime = Date.now()
      this.moved = false
    },
    onTouchMove(event) {
      const touch = event.changedTouches && event.changedTouches[0]
      if (!touch) return
      const deltaX = Math.abs(touch.clientX - this.startX)
      const deltaY = Math.abs(touch.clientY - this.startY)
      this.moved = deltaX > 6 || deltaY > 6
      this.pendingX = this.clamp(touch.clientX - this.dragOffsetX, 4, this.windowWidth - this.buttonSize - 4)
      this.pendingY = this.clamp(touch.clientY - this.dragOffsetY, 12, this.windowHeight - this.buttonSize - 8)
      this.schedulePositionUpdate()
    },
    onTouchEnd(event) {
      const touch = event.changedTouches && event.changedTouches[0]
      if (touch) {
        const deltaX = Math.abs(touch.clientX - this.startX)
        const deltaY = Math.abs(touch.clientY - this.startY)
        this.moved = deltaX > 8 || deltaY > 8
      }
      this.flushPositionUpdate()
      try {
        uni.setStorageSync('floating_action_position', { x: this.x, y: this.y })
      } catch (e) {}
    },
    schedulePositionUpdate() {
      if (this.dragFrame) return
      const flush = () => {
        this.dragFrame = null
        this.flushPositionUpdate()
      }
      this.dragFrame = typeof requestAnimationFrame === 'function'
        ? requestAnimationFrame(flush)
        : setTimeout(flush, 16)
    },
    flushPositionUpdate() {
      if (typeof this.pendingX !== 'number' || typeof this.pendingY !== 'number') return
      this.x = this.pendingX
      this.y = this.pendingY
    },
    handleTap() {
      if (this.moved) return
      if (Date.now() - this.startTime > 260) return
      smoothNavigateTo(this.url)
    }
  }
}
</script>

<style scoped>
.fab-view {
  position: fixed !important;
  left: 0;
  top: 0;
  width: 108rpx;
  height: 108rpx;
  border-radius: 50%;
  z-index: 99999;
  touch-action: none;
  will-change: transform;
  overflow: visible;
  background: transparent;
}
.fab-core {
  position: relative;
  width: 108rpx;
  height: 108rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #10B981 0%, #0D9488 58%, #2563EB 100%);
  box-shadow: 0 16rpx 36rpx rgba(13, 148, 136, 0.35);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 6rpx solid rgba(255, 255, 255, 0.86);
}
.fab-glow {
  position: absolute;
  top: 16rpx;
  right: 20rpx;
  width: 18rpx;
  height: 18rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.8);
}
.fab-main {
  font-size: 30rpx;
  line-height: 1;
  color: #FFFFFF;
  font-weight: 800;
  letter-spacing: 1rpx;
}
.fab-sub {
  margin-top: 6rpx;
  font-size: 18rpx;
  line-height: 1;
  color: rgba(255, 255, 255, 0.88);
  font-weight: 700;
}
</style>

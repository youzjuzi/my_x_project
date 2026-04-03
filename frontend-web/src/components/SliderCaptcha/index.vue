<template>
  <div class="slider-captcha-container">
    <div class="slider-box" ref="sliderBox" :class="{ success: isSuccess }">
      <!-- 背景文字 -->
      <div class="slider-text">{{ isSuccess ? '验证通过' : '请按住滑块，拖动到最右边' }}</div>
      
      <!-- 滑块背景 (绿色进度条) -->
      <div class="slider-bg" :style="{ width: sliderWidth + 'px' }"></div>
      
      <!-- 滑块按钮 -->
      <div 
        class="slider-btn" 
        ref="sliderBtn"
        :style="{ left: sliderLeft + 'px' }"
        @mousedown="startDrag"
        @touchstart="startDrag"
      >
        <el-icon v-if="isSuccess"><CircleCheckFilled /></el-icon>
        <el-icon v-else><DArrowRight /></el-icon>
      </div>
    </div>
    
    <!-- 为了兼容旧接口调用的隐藏弹窗逻辑 (可选，如果父组件是直接引用则不需要) -->
    <!-- 这里假设父组件是直接使用该组件作为内嵌元素 -->
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { ElMessage } from 'element-plus';
import { DArrowRight, CircleCheckFilled } from '@element-plus/icons-vue';
import { generateCaptcha, verifyCaptcha } from '@/api/captcha';

export default defineComponent({
  name: 'SliderCaptcha',
  components: {
    DArrowRight,
    CircleCheckFilled
  },
  emits: ['success', 'fail'],
  data() {
    return {
      isDragging: false,
      startX: 0,
      sliderLeft: 0,
      sliderWidth: 0,
      boxWidth: 0,
      maxLeft: 0,
      isSuccess: false,
      captchaId: '',
      hasShownDragHint: false
    };
  },
  mounted() {
    this.init();
    // 监听窗口大小变化
    window.addEventListener('resize', this.reset);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.reset);
    this.unbindEvents();
  },
  methods: {
    async init() {
      // 获取容器宽度
      if (this.$refs.sliderBox) {
        this.boxWidth = (this.$refs.sliderBox as HTMLElement).clientWidth;
        // 减去滑块按钮的宽度 (假设50px)
        this.maxLeft = this.boxWidth - 50;
      }
      
      // 在初始化时获取验证码ID (Token)
      this.refreshCaptcha();
    },
    
    async refreshCaptcha() {
      this.reset();
      try {
        const res: any = await generateCaptcha();
        if (res.code === 20000 && res.data) {
          this.captchaId = res.data.id;
        }
      } catch (error) {
        console.error('获取验证码失败', error);
      }
    },

    startDrag(e: MouseEvent | TouchEvent) {
      if (this.isSuccess) return;
      if (!this.hasShownDragHint) {
        ElMessage.info('请拖动滑块到最右侧完成验证');
        this.hasShownDragHint = true;
      }
      
      this.isDragging = true;
      const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
      this.startX = clientX;
      
      document.addEventListener('mousemove', this.onDrag);
      document.addEventListener('mouseup', this.stopDrag);
      document.addEventListener('touchmove', this.onDrag);
      document.addEventListener('touchend', this.stopDrag);
    },

    onDrag(e: MouseEvent | TouchEvent) {
      if (!this.isDragging) return;
      
      const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
      let moveX = clientX - this.startX;
      
      if (moveX < 0) moveX = 0;
      if (moveX > this.maxLeft) moveX = this.maxLeft;
      
      this.sliderLeft = moveX;
      this.sliderWidth = moveX;
    },

    async stopDrag() {
      if (!this.isDragging) return;
      this.isDragging = false;
      this.unbindEvents();

      // 判断是否滑到了最右边 (允许一点点误差，比如2px)
      if (this.sliderLeft >= this.maxLeft - 2) {
        this.sliderLeft = this.maxLeft;
        this.sliderWidth = this.maxLeft;
        await this.verify();
      } else {
        // 回弹
        this.sliderLeft = 0;
        this.sliderWidth = 0;
      }
    },
    
    unbindEvents() {
      document.removeEventListener('mousemove', this.onDrag);
      document.removeEventListener('mouseup', this.stopDrag);
      document.removeEventListener('touchmove', this.onDrag);
      document.removeEventListener('touchend', this.stopDrag);
    },

    async verify() {
      try {
        // 调用后端验证接口
        // 这里的 data 传空即可，因为后端现在通过 Redis Key 只验证 ID 存在性
        const res: any = await verifyCaptcha(this.captchaId, { x: this.sliderLeft });
        
        if (res.code === 20000) {
          this.isSuccess = true;
          ElMessage.success('滑动验证已通过，请继续操作');
          this.$emit('success', this.captchaId);
        } else {
          this.$emit('fail');
          this.reset();
          this.refreshCaptcha(); // 失败后刷新 Token
        }
      } catch (error) {
        this.$emit('fail');
        this.reset();
        this.refreshCaptcha();
      }
    },

    reset() {
      this.isDragging = false;
      this.sliderLeft = 0;
      this.sliderWidth = 0;
      this.isSuccess = false;
      this.hasShownDragHint = false;
      // 重新计算容器宽度 (防止窗口缩放)
      if (this.$refs.sliderBox) {
        this.boxWidth = (this.$refs.sliderBox as HTMLElement).clientWidth;
        this.maxLeft = this.boxWidth - 50;
      }
    },
    
    // 提供给父组件调用的方法，用于在外部重置验证码
    resetCaptcha() {
        this.refreshCaptcha();
    }
  }
});
</script>

<style lang="scss" scoped>
.slider-captcha-container {
  width: 100%;
  padding: 10px 0;
}

.slider-box {
  position: relative;
  width: 100%;
  height: 40px;
  background-color: #e8e8e8;
  border-radius: 4px;
  box-shadow: inset 0 0 2px #ccc;
  user-select: none;
  overflow: hidden;
  
  &.success {
    .slider-bg {
       background-color: #52ccba; // 成功时的颜色
    }
    .slider-btn {
        border-color: #52ccba;
        background-color: #fff;
        color: #52ccba;
    }
    .slider-text {
        color: #fff;
    }
  }
}

.slider-text {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  line-height: 40px;
  text-align: center;
  font-size: 14px;
  color: #666;
  z-index: 1;
  pointer-events: none; // 防止文字阻挡鼠标事件
}

.slider-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 0;
  height: 100%;
  background-color: #7ac23c;
  z-index: 2;
  transition: background-color 0.3s;
}

.slider-btn {
  position: absolute;
  top: 0;
  left: 0;
  width: 50px;
  height: 40px;
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  box-shadow: 0 0 5px rgba(0,0,0,0.1);
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.3s;
  
  &:hover {
    background-color: #f5f5f5;
  }
  
  .el-icon {
    font-size: 20px;
    color: #666;
  }
}
</style>



<template>
  <div class="prompt-manager-container p-5">
    <div class="card bg-base-100 shadow-md">
      <div class="card-body">
        <!-- Tabs 导航 -->
        <nav class="tabs tabs-bordered" aria-label="提示词工具" role="tablist" aria-orientation="horizontal">
          <button 
            type="button" 
            class="tab active-tab:tab-active active" 
            id="tab-translator" 
            data-tab="#translator-panel" 
            aria-controls="translator-panel" 
            role="tab" 
            aria-selected="true"
          >
            快速翻译
          </button>
          <button 
            type="button" 
            class="tab active-tab:tab-active" 
            id="tab-badges" 
            data-tab="#badges-panel" 
            aria-controls="badges-panel" 
            role="tab" 
            aria-selected="false"
          >
            提示词拆分
          </button>
        </nav>
        
        <!-- Tabs 内容 -->
        <div class="mt-4">
          <!-- 快速翻译面板 -->
          <div id="translator-panel" role="tabpanel" aria-labelledby="tab-translator">
            <QuickTranslator />
          </div>
          
          <!-- 提示词拆分面板 -->
          <div id="badges-panel" class="hidden" role="tabpanel" aria-labelledby="tab-badges">
            <PromptBadges />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted } from 'vue';
import QuickTranslator from '../components/Translator.vue';
import PromptBadges from '../components/PromptBadges.vue';

// 声明全局HSTabs类型
declare global {
  interface Window {
    HSTabs: {
      getInstance: (selector: string, isInstance?: boolean) => any;
      open: (element: HTMLElement) => void;
    }
  }
}

export default defineComponent({
  name: 'PromptManager',
  
  components: {
    QuickTranslator,
    PromptBadges
  },
  
  setup() {
    // 组件挂载后初始化tabs
    onMounted(() => {
      // FlyonUI的Tabs组件会自动初始化
    });
  }
});
</script>

<style scoped>
/* 使用Tailwind实现，无需额外样式 */
</style> 
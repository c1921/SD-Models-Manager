<template>
  <div class="prompt-manager-container p-5">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- 快速翻译工具 -->
      <div class="card bg-base-100 shadow-md">
        <div class="card-body">
          <h2 class="card-title text-xl mb-2">快速翻译</h2>
          <QuickTranslator />
        </div>
      </div>
      
      <!-- 提示词拆分工具 -->
      <div class="card bg-base-100 shadow-md">
        <div class="card-body">
          <h2 class="card-title text-xl mb-2">提示词拆分</h2>
          <PromptBadges />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import QuickTranslator from '../components/Translator.vue';
import PromptBadges from '../components/PromptBadges.vue';

export default defineComponent({
  name: 'PromptManager',
  
  components: {
    QuickTranslator,
    PromptBadges
  }
});
</script>

<style scoped>
/* 使用Tailwind实现，无需额外样式 */
</style> 
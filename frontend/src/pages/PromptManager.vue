<template>
  <div class="prompt-manager-container p-5">
    <!-- 快速翻译工具 -->
    <QuickTranslator />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import QuickTranslator from '../components/Translator.vue';

export default defineComponent({
  name: 'PromptManager',
  
  components: {
    QuickTranslator
  }
});
</script>

<style scoped>
/* 使用Tailwind实现，无需额外样式 */
</style> 
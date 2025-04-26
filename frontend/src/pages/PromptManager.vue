<template>
  <div class="prompt-manager-container p-5">
    <div class="card bg-base-100 shadow-md">
      <div class="card-body p-3 sm:p-5">
        <!-- Tabs 导航 -->
        <nav class="tabs tabs-bordered w-full" aria-label="提示词工具" role="tablist" aria-orientation="horizontal">
          <button 
            type="button" 
            class="tab tab-lg flex-1 active-tab:tab-active active px-2 sm:px-4" 
            id="tab-badges" 
            data-tab="#badges-panel" 
            aria-controls="badges-panel" 
            role="tab" 
            aria-selected="true"
          >
            <span class="icon-[tabler--reorder] inline-block size-5 sm:me-1.5"></span>
            <span class="hidden sm:inline">提示词排序</span>
            <span class="sm:hidden" aria-label="提示词排序"></span>
          </button>
          <button 
            type="button" 
            class="tab tab-lg flex-1 active-tab:tab-active px-2 sm:px-4" 
            id="tab-library-editor" 
            data-tab="#library-editor-panel" 
            aria-controls="library-editor-panel" 
            role="tab" 
            aria-selected="false"
          >
            <span class="icon-[tabler--edit] inline-block size-5 sm:me-1.5"></span>
            <span class="hidden sm:inline">提示词库编辑</span>
            <span class="sm:hidden" aria-label="提示词库编辑"></span>
          </button>
          <button 
            type="button" 
            class="tab tab-lg flex-1 active-tab:tab-active px-2 sm:px-4" 
            id="tab-translator" 
            data-tab="#translator-panel" 
            aria-controls="translator-panel" 
            role="tab" 
            aria-selected="false"
          >
            <span class="icon-[tabler--language] inline-block size-5 sm:me-1.5"></span>
            <span class="hidden sm:inline">快速翻译</span>
            <span class="sm:hidden" aria-label="快速翻译"></span>
          </button>
        </nav>
        
        <!-- Tabs 内容 -->
        <div class="mt-4">
          <!-- 提示词排序面板 -->
          <div id="badges-panel" role="tabpanel" aria-labelledby="tab-badges">
            <PromptBadges 
              :promptLibraryData="promptLibrary"
              :key="promptLibraryKey"
            />
          </div>
          
          <!-- 提示词库编辑面板 -->
          <div id="library-editor-panel" class="hidden" role="tabpanel" aria-labelledby="tab-library-editor">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <!-- 左侧：提示词编辑器 -->
              <div>
                <h3 class="text-lg mb-4">添加提示词</h3>
                <PromptLibraryEditor 
                  :promptLibraryData="promptLibrary"
                  :selectedPrompt="selectedPrompt"
                  @saved="handlePromptLibrarySaved"
                />
              </div>
              
              <!-- 右侧：提示词库显示 -->
              <div>
                <h3 class="text-lg mb-4">提示词库</h3>
                <PromptLibrary 
                  :key="promptLibraryKey"
                  :promptLibraryData="promptLibrary"
                  @select-prompt="handleSelectPrompt"
                />
              </div>
            </div>
          </div>
          
          <!-- 快速翻译面板 -->
          <div id="translator-panel" class="hidden" role="tabpanel" aria-labelledby="tab-translator">
            <QuickTranslator />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref, nextTick } from 'vue';
import QuickTranslator from '../components/Translator.vue';
import PromptBadges from '../components/PromptBadges.vue';
import PromptLibraryEditor from '../components/PromptLibraryEditor.vue';
import PromptLibrary from '../components/PromptLibrary.vue';
import { PromptsAPI } from '../api/prompts';
import type { PromptLibraryItem } from '../api/prompts';

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
    PromptBadges,
    PromptLibraryEditor,
    PromptLibrary
  },
  
  setup() {
    // 提示词库数据
    const promptLibrary = ref<PromptLibraryItem[]>([]);
    // 提示词库刷新标识
    const promptLibraryKey = ref(0);
    // 选中的提示词
    const selectedPrompt = ref<PromptLibraryItem | null>(null);
    
    // 加载提示词库
    const loadPromptLibrary = async () => {
      try {
        // 从后端获取提示词库
        const data = await PromptsAPI.getPromptLibrary();
        promptLibrary.value = data;
        
        console.log('[提示词库] 加载成功，数量:', data.length);
      } catch (error) {
        console.error('加载提示词库失败:', error);
        
        // 加载失败时使用空数组
        promptLibrary.value = [];
      }
    };
    
    // 处理新提示词添加成功
    const handlePromptLibrarySaved = async (newPrompt: PromptLibraryItem) => {
      try {
        // 重新加载提示词库数据
        const data = await PromptsAPI.getPromptLibrary();
        promptLibrary.value = data;
        
        // 增加key值，强制刷新提示词库组件
        promptLibraryKey.value++;
        
        console.log('[提示词库] 更新成功，数量:', data.length);
        
        // 通知所有子组件数据已更新
        nextTick(() => {
          // 这里不需要额外操作，因为Vue的响应式系统会自动处理
          console.log('[提示词库] 已通知所有子组件更新');
        });
      } catch (error) {
        console.error('更新提示词库失败:', error);
        // 如果更新失败，至少添加新提示词到本地
        promptLibrary.value.push(newPrompt);
        promptLibraryKey.value++;
      }
    };
    
    // 处理选择提示词
    const handleSelectPrompt = (prompt: PromptLibraryItem) => {
      // 这里可以添加选择提示词后的逻辑，比如填充到编辑器
      selectedPrompt.value = prompt;
    };
    
    // 组件挂载后初始化tabs
    onMounted(() => {
      // 加载提示词库数据
      loadPromptLibrary();
      
      // FlyonUI的Tabs组件会自动初始化
    });
    
    return {
      promptLibrary,
      promptLibraryKey,
      selectedPrompt,
      handlePromptLibrarySaved,
      handleSelectPrompt
    };
  }
});
</script>

<style scoped>
/* 使用Tailwind实现，无需额外样式 */
</style> 
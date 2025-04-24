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
          <button 
            type="button" 
            class="tab active-tab:tab-active" 
            id="tab-library-editor" 
            data-tab="#library-editor-panel" 
            aria-controls="library-editor-panel" 
            role="tab" 
            aria-selected="false"
          >
            提示词库编辑
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
          
          <!-- 提示词库编辑面板 -->
          <div id="library-editor-panel" class="hidden" role="tabpanel" aria-labelledby="tab-library-editor">
            <PromptLibraryEditor 
              :promptLibraryData="promptLibrary"
              @saved="handlePromptLibrarySaved"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref } from 'vue';
import QuickTranslator from '../components/Translator.vue';
import PromptBadges from '../components/PromptBadges.vue';
import PromptLibraryEditor from '../components/PromptLibraryEditor.vue';
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
    PromptLibraryEditor
  },
  
  setup() {
    // 提示词库数据
    const promptLibrary = ref<PromptLibraryItem[]>([]);
    
    // 加载提示词库
    const loadPromptLibrary = async () => {
      try {
        // 从后端获取提示词库
        const data = await PromptsAPI.getPromptLibrary();
        promptLibrary.value = data;
        
        console.log('[提示词库] 加载成功，数量:', data.length);
      } catch (error) {
        console.error('加载提示词库失败:', error);
        
        // 加载失败时使用示例数据
        promptLibrary.value = [
          {
            id: '1',
            text: '写实风格',
            chinese: '写实风格',
            english: 'realistic style',
            category: '风格',
            subCategory: '基础风格'
          },
          {
            id: '2',
            text: '水彩画',
            chinese: '水彩画',
            english: 'watercolor',
            category: '风格',
            subCategory: '绘画媒介'
          },
          {
            id: '3',
            text: '高清',
            chinese: '高清',
            english: 'high resolution',
            category: '质量',
            subCategory: '分辨率'
          },
          {
            id: '4',
            text: 'masterpiece',
            chinese: '杰作',
            english: 'masterpiece',
            category: '质量',
            subCategory: '通用'
          }
        ];
      }
    };
    
    // 处理新提示词添加成功
    const handlePromptLibrarySaved = (newPrompt: PromptLibraryItem) => {
      // 添加到本地提示词库列表
      promptLibrary.value.push(newPrompt);
    };
    
    // 组件挂载后初始化tabs
    onMounted(() => {
      // 加载提示词库数据
      loadPromptLibrary();
      
      // FlyonUI的Tabs组件会自动初始化
    });
    
    return {
      promptLibrary,
      handlePromptLibrarySaved
    };
  }
});
</script>

<style scoped>
/* 使用Tailwind实现，无需额外样式 */
</style> 
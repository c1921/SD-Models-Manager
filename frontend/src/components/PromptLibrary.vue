<template>
  <div class="prompt-library">
    <!-- 提示词库 -->
    <div class="mb-4">
      <div class="flex justify-between items-center mb-2">
        <label class="block text-sm font-medium">提示词库</label>
      </div>
      <div class="flex flex-wrap gap-2 bg-base-200 p-3 rounded-md">
        <!-- 加载状态 -->
        <div v-if="isLoading" class="text-center text-base-content/50 py-6 w-full flex justify-center items-center">
          <i class="icon-[tabler--loader-2] animate-spin mr-2"></i> 正在加载提示词库...
        </div>
        
        <!-- 错误信息 -->
        <div v-else-if="errorMessage" class="text-center text-error py-6 w-full">
          <i class="icon-[tabler--alert-circle] mr-2"></i> {{ errorMessage }}
        </div>
        
        <!-- 空状态 -->
        <div v-else-if="promptLibraryFiltered.length === 0" class="text-center text-base-content/50 py-6 w-full">
          暂无提示词，请添加或选择分类
        </div>
        
        <!-- 提示词列表 -->
        <div v-else class="flex flex-wrap gap-2 w-full">
          <!-- 分类选择 -->
          <div class="w-full mb-2 flex gap-2 flex-wrap">
            <div class="dropdown">
              <label tabindex="0" class="btn btn-sm">
                {{ selectedCategory || '选择一级分类' }}
                <i class="icon-[tabler--chevron-down]"></i>
              </label>
              <ul tabindex="0" class="dropdown-content z-[1] menu shadow bg-base-100 rounded-box w-52">
                <li><a @click="selectedCategory = ''">全部</a></li>
                <li v-for="category in categories" :key="category">
                  <a @click="selectedCategory = category">{{ category }}</a>
                </li>
              </ul>
            </div>
            
            <div class="dropdown" v-if="selectedCategory">
              <label tabindex="0" class="btn btn-sm">
                {{ selectedSubCategory || '选择二级分类' }}
                <i class="icon-[tabler--chevron-down]"></i>
              </label>
              <ul tabindex="0" class="dropdown-content z-[1] menu shadow bg-base-100 rounded-box w-52">
                <li><a @click="selectedSubCategory = ''">全部</a></li>
                <li v-for="subCategory in subCategories" :key="subCategory">
                  <a @click="selectedSubCategory = subCategory">{{ subCategory }}</a>
                </li>
              </ul>
            </div>
          </div>
          
          <!-- 提示词列表 -->
          <button 
            v-for="(prompt, index) in promptLibraryFiltered" 
            :key="'lib-prompt-' + index"
            class="badge badge-lg badge-secondary h-auto cursor-pointer"
            @click="selectPrompt(prompt)"
          >
            <div class="text-sm">{{ prompt.chinese }}</div>
            <div class="text-xs opacity-80">{{ prompt.english }}</div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import { PromptsAPI } from '../api/prompts';
import type { PromptLibraryItem } from '../api/prompts';

export default defineComponent({
  name: 'PromptLibrary',
  
  emits: ['select-prompt'],
  
  setup(props, { emit }) {
    // 提示词库相关
    const promptLibrary = ref<PromptLibraryItem[]>([]);
    const selectedCategory = ref('');
    const selectedSubCategory = ref('');
    const isLoading = ref(false);
    const errorMessage = ref('');
    
    // 一级分类列表
    const categories = computed(() => {
      const categorySet = new Set(promptLibrary.value.map(item => item.category));
      return Array.from(categorySet).sort();
    });
    
    // 二级分类列表 (根据选择的一级分类筛选)
    const subCategories = computed(() => {
      let items = promptLibrary.value;
      
      // 按页面中选择的一级分类筛选
      if (selectedCategory.value) {
        items = items.filter(item => item.category === selectedCategory.value);
      }
      
      const subCategorySet = new Set(items.map(item => item.subCategory));
      return Array.from(subCategorySet).sort();
    });
    
    // 过滤后的提示词库
    const promptLibraryFiltered = computed(() => {
      let filtered = promptLibrary.value;
      
      if (selectedCategory.value) {
        filtered = filtered.filter(item => item.category === selectedCategory.value);
        
        if (selectedSubCategory.value) {
          filtered = filtered.filter(item => item.subCategory === selectedSubCategory.value);
        }
      }
      
      return filtered;
    });
    
    // 选择提示词 - 发送到父组件
    const selectPrompt = (prompt: PromptLibraryItem) => {
      emit('select-prompt', prompt);
    };
    
    // 加载提示词库
    const loadPromptLibrary = async () => {
      try {
        isLoading.value = true;
        errorMessage.value = '';
        
        // 从后端获取提示词库
        const data = await PromptsAPI.getPromptLibrary();
        promptLibrary.value = data;
        
        console.log('[提示词库] 加载成功，数量:', data.length);
      } catch (error) {
        console.error('加载提示词库失败:', error);
        errorMessage.value = '加载提示词库失败，请刷新页面重试';
        
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
      } finally {
        isLoading.value = false;
      }
    };
    
    // 组件挂载后初始化
    onMounted(() => {
      // 加载提示词库
      loadPromptLibrary();
    });
    
    return {
      // 提示词库相关
      promptLibrary,
      promptLibraryFiltered,
      selectedCategory,
      selectedSubCategory,
      categories,
      subCategories,
      selectPrompt,
      isLoading,
      errorMessage,
    };
  }
});
</script>

<style scoped>
/* 可添加组件特定样式 */
</style> 
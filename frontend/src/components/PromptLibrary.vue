<template>
  <div class="prompt-library">
    <!-- 提示词库 -->
    <div class="mb-4">
      <div class="flex justify-between items-center mb-2">
        <label class="block text-sm font-medium">提示词库</label>
      </div>
      <div class="bg-base-200 p-3 rounded-md">
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
        <div v-else class="w-full">
          <!-- 分类选择 -->
          <div class="mb-4">
            <div class="tabs tabs-bordered">
              <!-- 全部分类选项 -->
              <button 
                class="tab" 
                :class="{'tab-active': selectedCategory === ''}"
                @click="selectCategory('')"
              >
                全部
              </button>
              
              <!-- 一级分类选项 -->
              <button 
                v-for="category in categories" 
                :key="category"
                class="tab" 
                :class="{'tab-active': selectedCategory === category}"
                @click="selectCategory(category)"
              >
                {{ category }}
              </button>
            </div>
            
            <!-- 二级分类选择 -->
            <div v-if="selectedCategory && subCategories.length > 0" class="mt-2">
              <div class="badge-group flex flex-wrap gap-2 mt-2">
                <!-- 全部二级分类选项 -->
                <button 
                  class="badge badge-outline" 
                  :class="{'badge-primary': selectedSubCategory === ''}"
                  @click="selectedSubCategory = ''"
                >
                  全部
                </button>
                
                <!-- 二级分类选项 -->
                <button 
                  v-for="subCategory in subCategories" 
                  :key="subCategory"
                  class="badge badge-outline" 
                  :class="{'badge-primary': selectedSubCategory === subCategory}"
                  @click="selectedSubCategory = subCategory"
                >
                  {{ subCategory }}
                </button>
              </div>
            </div>
          </div>
          
          <!-- 提示词列表 -->
          <div class="flex flex-wrap gap-2">
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
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue';
import type { PromptLibraryItem } from '../api/prompts';

export default defineComponent({
  name: 'PromptLibrary',
  
  emits: ['select-prompt'],
  
  props: {
    promptLibraryData: {
      type: Array as () => PromptLibraryItem[],
      default: () => [],
      required: true
    }
  },
  
  setup(props, { emit }) {
    // 提示词库相关
    const promptLibrary = ref<PromptLibraryItem[]>(props.promptLibraryData);
    const selectedCategory = ref('');
    const selectedSubCategory = ref('');
    const isLoading = ref(false);
    const errorMessage = ref('');
    
    // 监听提示词库数据变化
    watch(() => props.promptLibraryData, (newData) => {
      console.log('[PromptLibrary] 提示词库数据更新:', newData.length);
      promptLibrary.value = newData;
    }, { deep: true, immediate: true });
    
    // 监听一级分类变化，当一级分类变化时重置二级分类选择
    watch(selectedCategory, () => {
      // 重置二级分类
      selectedSubCategory.value = '';
    });
    
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
    
    // 选择一级分类
    const selectCategory = (category: string) => {
      // 如果选择相同的分类，不做处理
      if (selectedCategory.value === category) return;
      
      // 更新选择的一级分类
      selectedCategory.value = category;
      // 重置二级分类选择
      selectedSubCategory.value = '';
    };
    
    // 加载提示词库
    const loadPromptLibrary = async () => {
      try {
        isLoading.value = true;
        errorMessage.value = '';
        
        // 数据现在从父组件传入，不需要再调用API
        console.log('[提示词库] 从父组件加载数据，数量:', promptLibrary.value.length);
      } catch (error) {
        console.error('加载提示词库失败:', error);
        errorMessage.value = '加载提示词库失败，请刷新页面重试';
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
      selectCategory,
      isLoading,
      errorMessage,
    };
  }
});
</script>

<style scoped>
/* 可添加组件特定样式 */
</style> 
<template>
  <div class="prompt-manager-container p-5">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold">提示词管理</h2>
      <div class="flex items-center">
        <button class="btn btn-primary mr-2" @click="openCreateModal">
          <i class="icon-[tabler--plus] mr-1.5 size-5"></i> 新建提示词
        </button>
        <div class="relative">
          <input 
            type="text" 
            class="input input-bordered w-full max-w-xs" 
            placeholder="搜索提示词..." 
            v-model="searchQuery"
            @input="handleSearch"
          >
          <button class="btn btn-ghost btn-sm absolute right-1 top-1/2 -translate-y-1/2">
            <i class="icon-[tabler--search] size-5"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 快速翻译工具 -->
    <div class="card bg-base-100 shadow-md mb-6">
      <div class="card-body p-4">
        <h3 class="card-title text-lg mb-2">
          <i class="icon-[tabler--language] mr-2"></i>
          快速翻译
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="form-control">
            <div class="flex items-center mb-1">
              <label class="label-text font-medium">输入文本</label>
              <div class="ml-2">
                <button 
                  class="btn btn-xs" 
                  :class="quickTranslateDirection ? 'btn-primary' : ''"
                  @click="quickTranslateDirection = true"
                >
                  中→英
                </button>
                <button 
                  class="btn btn-xs ml-1" 
                  :class="!quickTranslateDirection ? 'btn-primary' : ''"
                  @click="quickTranslateDirection = false"
                >
                  英→中
                </button>
              </div>
            </div>
            <textarea 
              class="textarea textarea-bordered w-full h-28" 
              v-model="quickTranslateInput"
              :placeholder="quickTranslateDirection ? '输入中文内容' : 'Enter English content'"
            ></textarea>
          </div>
          <div class="form-control">
            <label class="label-text font-medium mb-1">翻译结果</label>
            <div class="relative">
              <textarea 
                class="textarea textarea-bordered w-full h-28" 
                v-model="quickTranslateOutput"
                readonly
                placeholder="翻译结果将显示在这里"
              ></textarea>
              <button 
                class="btn btn-sm btn-circle absolute right-2 top-2"
                @click="copyTranslationToClipboard"
                v-if="quickTranslateOutput"
                title="复制到剪贴板"
              >
                <i class="icon-[tabler--copy]"></i>
              </button>
            </div>
          </div>
        </div>
        <div class="flex justify-end mt-2">
          <button 
            class="btn btn-primary"
            @click="performQuickTranslation"
            :disabled="isQuickTranslating || !quickTranslateInput"
          >
            <i class="icon-[tabler--language] mr-1.5"></i>
            {{ isQuickTranslating ? '翻译中...' : '翻译' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 分类筛选 -->
    <div class="mb-4">
      <div class="flex flex-wrap gap-2">
        <button 
          class="btn" 
          :class="selectedCategory === '' ? 'btn-primary' : 'btn-outline'"
          @click="filterByCategory('')"
        >
          全部
        </button>
        <button 
          v-for="category in categories" 
          :key="category"
          class="btn" 
          :class="selectedCategory === category ? 'btn-primary' : 'btn-outline'"
          @click="filterByCategory(category)"
        >
          {{ category }}
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-12">
      <div class="loading loading-spinner loading-lg"></div>
      <p class="mt-2 text-base-content/70">正在加载提示词...</p>
    </div>

    <!-- 提示词列表 -->
    <div v-else-if="filteredPrompts.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="prompt in filteredPrompts" :key="prompt.id" class="card bg-base-100 shadow-md h-full">
        <div class="card-header p-3 flex justify-between items-center">
          <h3 class="card-title text-lg m-0">{{ prompt.title }}</h3>
          <div>
            <button class="btn btn-ghost btn-sm text-error" @click="toggleFavorite(prompt)">
              <i class="icon-[tabler--heart]" :class="prompt.favorite ? 'fill-current' : ''"></i>
            </button>
          </div>
        </div>
        <div class="card-body p-4">
          <p class="mb-1"><strong>分类:</strong> {{ prompt.category }}</p>
          <div class="mb-3 flex flex-wrap gap-1">
            <span 
              v-for="tag in prompt.tags" 
              :key="tag" 
              class="badge badge-neutral"
            >
              {{ tag }}
            </span>
          </div>
          
          <!-- 内容显示 -->
          <div class="mb-3">
            <div class="flex justify-between items-center mb-2">
              <div class="join">
                <button 
                  class="join-item btn btn-sm" 
                  :class="contentMode === 'en' ? 'btn-active' : ''"
                  @click="contentMode = 'en'"
                >
                  英文
                </button>
                <button 
                  class="join-item btn btn-sm" 
                  :class="contentMode === 'zh' ? 'btn-active' : ''"
                  @click="contentMode = 'zh'"
                >
                  中文
                </button>
              </div>
              <button 
                class="btn btn-sm btn-outline" 
                @click="translatePrompt(prompt)"
                :disabled="isTranslating"
              >
                <i class="icon-[tabler--language] mr-1"></i>
                {{ isTranslating ? '翻译中...' : '翻译' }}
              </button>
            </div>
            
            <div class="rounded-md border bg-base-200 p-2 overflow-y-auto max-h-36 whitespace-pre-wrap">
              <p v-if="contentMode === 'en'">
                {{ prompt.content || '暂无英文内容' }}
              </p>
              <p v-else>
                {{ prompt.content_zh || '暂无中文内容' }}
              </p>
            </div>
          </div>
        </div>
        <div class="card-footer p-3 flex justify-between">
          <button class="btn btn-sm btn-outline" @click="openEditModal(prompt)">
            <i class="icon-[tabler--edit] mr-1"></i> 编辑
          </button>
          <button class="btn btn-sm btn-error btn-outline" @click="confirmDelete(prompt)">
            <i class="icon-[tabler--trash] mr-1"></i> 删除
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="text-center py-12">
      <p class="text-base-content/70">还没有提示词，点击"新建提示词"按钮创建第一个提示词。</p>
    </div>

    <!-- 创建/编辑提示词模态框 -->
    <div v-if="isPromptModalOpen" class="modal modal-open">
      <div class="modal-box max-w-3xl">
        <h3 class="font-bold text-lg mb-4">{{ isEditing ? '编辑提示词' : '新建提示词' }}</h3>
        <button 
          class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2" 
          @click="closePromptModal"
        >✕</button>
        
        <form @submit.prevent="savePrompt">
          <div class="form-control mb-3">
            <label class="label">
              <span class="label-text">标题</span>
            </label>
            <input 
              type="text" 
              class="input input-bordered w-full" 
              v-model="currentPrompt.title" 
              required
            >
          </div>
          
          <div class="form-control mb-3">
            <label class="label">
              <span class="label-text">分类</span>
            </label>
            <div class="relative">
              <input 
                type="text" 
                class="input input-bordered w-full" 
                v-model="currentPrompt.category" 
                list="categoryList"
                required
              >
              <datalist id="categoryList">
                <option v-for="category in categories" :key="category" :value="category"></option>
              </datalist>
            </div>
          </div>
          
          <div class="form-control mb-3">
            <label class="label">
              <span class="label-text">标签 (用逗号分隔)</span>
            </label>
            <input 
              type="text" 
              class="input input-bordered w-full" 
              v-model="tagsInput"
            >
          </div>
          
          <div class="form-control mb-3">
            <label class="label">
              <span class="label-text">内容</span>
            </label>
            <textarea 
              class="textarea textarea-bordered h-40" 
              v-model="currentPrompt.content" 
              required
            ></textarea>
            <label class="label">
              <span class="label-text-alt">输入提示词内容，系统会自动检测输入语言并翻译。</span>
            </label>
          </div>
          
          <div class="form-control mb-3">
            <label class="label cursor-pointer justify-start gap-2">
              <input 
                type="checkbox" 
                class="checkbox" 
                v-model="autoTranslate"
              >
              <span class="label-text">自动翻译</span>
            </label>
          </div>
          
          <div v-if="translatedPreview" class="mb-3">
            <label class="label">
              <span class="label-text">翻译预览</span>
            </label>
            <div class="border rounded-md p-2 bg-base-200">
              {{ translatedPreview }}
            </div>
          </div>
          
          <div class="modal-action">
            <button type="button" class="btn" @click="closePromptModal">取消</button>
            <div class="flex gap-2">
              <button 
                type="button" 
                class="btn btn-outline" 
                @click="previewTranslation"
                :disabled="isTranslating || !currentPrompt.content"
              >
                <i class="icon-[tabler--language] mr-1"></i> 
                {{ isTranslating ? '翻译中...' : '预览翻译' }}
              </button>
              <button type="submit" class="btn btn-primary">保存</button>
            </div>
          </div>
        </form>
      </div>
      <div class="modal-backdrop" @click="closePromptModal"></div>
    </div>

    <!-- 删除确认模态框 -->
    <div v-if="isDeleteModalOpen" class="modal modal-open">
      <div class="modal-box">
        <h3 class="font-bold text-lg mb-4">确认删除</h3>
        <button 
          class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2" 
          @click="closeDeleteModal"
        >✕</button>
        <p>您确定要删除提示词 "{{ promptToDelete?.title }}" 吗？此操作无法撤销。</p>
        <div class="modal-action">
          <button type="button" class="btn" @click="closeDeleteModal">取消</button>
          <button type="button" class="btn btn-error" @click="deletePrompt">删除</button>
        </div>
      </div>
      <div class="modal-backdrop" @click="closeDeleteModal"></div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed, watch } from 'vue';
import { PromptsAPI } from '../api/prompts';
import type { Prompt, CreatePromptParams, UpdatePromptParams } from '../api/prompts';

export default defineComponent({
  name: 'PromptManager',
  
  setup() {
    // 状态
    const prompts = ref<Prompt[]>([]);
    const categories = ref<string[]>([]);
    const loading = ref(true);
    const isTranslating = ref(false);
    const searchQuery = ref('');
    const selectedCategory = ref('');
    const contentMode = ref<'en' | 'zh'>('zh'); // 默认显示中文
    
    // 快速翻译相关
    const quickTranslateInput = ref('');
    const quickTranslateOutput = ref('');
    const isQuickTranslating = ref(false);
    const quickTranslateDirection = ref(false); // false: 英→中, true: 中→英
    
    // 模态框相关
    const isEditing = ref(false);
    const isPromptModalOpen = ref(false);
    const isDeleteModalOpen = ref(false);
    const promptToDelete = ref<Prompt | null>(null);
    
    // 表单相关
    const currentPrompt = ref<CreatePromptParams>({
      title: '',
      content: '',
      category: '',
      tags: [],
    });
    const tagsInput = ref('');
    const autoTranslate = ref(true);
    const translatedPreview = ref('');
    
    // 获取所有提示词
    const fetchPrompts = async () => {
      loading.value = true;
      try {
        prompts.value = await PromptsAPI.getPrompts();
      } catch (error) {
        console.error('获取提示词失败', error);
      } finally {
        loading.value = false;
      }
    };
    
    // 获取所有分类
    const fetchCategories = async () => {
      try {
        categories.value = await PromptsAPI.getCategories();
      } catch (error) {
        console.error('获取分类失败', error);
      }
    };
    
    // 过滤提示词
    const filteredPrompts = computed(() => {
      let result = prompts.value;
      
      // 按分类过滤
      if (selectedCategory.value) {
        result = result.filter(p => p.category === selectedCategory.value);
      }
      
      // 按搜索词过滤
      if (searchQuery.value.trim()) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(p => 
          p.title.toLowerCase().includes(query) || 
          p.content.toLowerCase().includes(query) || 
          p.content_zh.toLowerCase().includes(query) ||
          p.tags.some(tag => tag.toLowerCase().includes(query))
        );
      }
      
      return result;
    });
    
    // 按分类筛选
    const filterByCategory = (category: string) => {
      selectedCategory.value = category;
    };
    
    // 搜索处理
    const handleSearch = () => {
      // 可以在这里添加防抖逻辑
    };
    
    // 切换收藏状态
    const toggleFavorite = async (prompt: Prompt) => {
      try {
        const newState = await PromptsAPI.toggleFavorite(prompt.id);
        prompt.favorite = newState;
      } catch (error) {
        console.error('切换收藏状态失败', error);
      }
    };
    
    // 翻译提示词
    const translatePrompt = async (prompt: Prompt) => {
      if (isTranslating.value) return;
      
      isTranslating.value = true;
      try {
        const updatedPrompt = await PromptsAPI.translatePrompt(prompt.id, true);
        
        // 更新本地数据
        if (updatedPrompt) {
          const index = prompts.value.findIndex(p => p.id === prompt.id);
          if (index !== -1) {
            prompts.value[index] = updatedPrompt;
          }
        }
      } catch (error: any) {
        console.error('翻译提示词失败', error);
        alert(`翻译失败: ${error.message || '未知错误'}`);
      } finally {
        isTranslating.value = false;
      }
    };
    
    // 执行快速翻译
    const performQuickTranslation = async () => {
      if (!quickTranslateInput.value || isQuickTranslating.value) return;
      
      isQuickTranslating.value = true;
      quickTranslateOutput.value = '';
      
      try {
        const result = await PromptsAPI.translateText(
          quickTranslateInput.value,
          quickTranslateDirection.value // true: 中→英, false: 英→中
        );
        
        if (result && result.translated) {
          quickTranslateOutput.value = result.translated;
        } else {
          quickTranslateOutput.value = '翻译失败: 无法获取翻译结果';
          console.error('翻译结果格式错误', result);
        }
      } catch (error: any) {
        console.error('快速翻译失败', error);
        quickTranslateOutput.value = `翻译失败: ${error.message || '未知错误'}`;
      } finally {
        isQuickTranslating.value = false;
      }
    };
    
    // 复制翻译结果到剪贴板
    const copyTranslationToClipboard = () => {
      if (!quickTranslateOutput.value) return;
      
      navigator.clipboard.writeText(quickTranslateOutput.value)
        .then(() => {
          // 可以在这里添加一个提示
          console.log('复制到剪贴板成功');
        })
        .catch(err => {
          console.error('复制到剪贴板失败', err);
        });
    };
    
    // 预览翻译
    const previewTranslation = async () => {
      if (!currentPrompt.value.content || isTranslating.value) return;
      
      isTranslating.value = true;
      translatedPreview.value = '';
      
      try {
        // 检测输入是中文还是英文
        const isChinese = /[\u4e00-\u9fa5]/.test(currentPrompt.value.content);
        
        const result = await PromptsAPI.translateText(
          currentPrompt.value.content,
          isChinese // 如果是中文，则翻译成英文
        );
        
        if (result && result.translated) {
          translatedPreview.value = result.translated;
        } else {
          translatedPreview.value = '翻译失败: 无法获取翻译结果';
          console.error('翻译结果格式错误', result);
        }
      } catch (error: any) {
        console.error('翻译预览失败', error);
        translatedPreview.value = `翻译失败: ${error.message || '未知错误'}`;
      } finally {
        isTranslating.value = false;
      }
    };
    
    // 打开创建模态框
    const openCreateModal = () => {
      isEditing.value = false;
      currentPrompt.value = {
        title: '',
        content: '',
        category: '',
        tags: [],
      };
      tagsInput.value = '';
      translatedPreview.value = '';
      isPromptModalOpen.value = true;
    };
    
    // 打开编辑模态框
    const openEditModal = (prompt: Prompt) => {
      isEditing.value = true;
      currentPrompt.value = {
        title: prompt.title,
        content: prompt.content || prompt.content_zh,
        category: prompt.category,
        tags: [...prompt.tags],
      };
      tagsInput.value = prompt.tags.join(', ');
      translatedPreview.value = '';
      isPromptModalOpen.value = true;
    };
    
    // 关闭提示词模态框
    const closePromptModal = () => {
      isPromptModalOpen.value = false;
    };
    
    // 关闭删除确认模态框
    const closeDeleteModal = () => {
      isDeleteModalOpen.value = false;
    };
    
    // 保存提示词
    const savePrompt = async () => {
      try {
        // 处理标签
        const tags = tagsInput.value
          .split(',')
          .map(tag => tag.trim())
          .filter(tag => tag);
        
        if (isEditing.value) {
          // 更新现有提示词
          const promptId = prompts.value.find(
            p => p.title === currentPrompt.value.title
          )?.id;
          
          if (promptId) {
            const params: UpdatePromptParams = {
              ...currentPrompt.value,
              tags,
              auto_translate: autoTranslate.value,
            };
            
            await PromptsAPI.updatePrompt(promptId, params);
          }
        } else {
          // 创建新提示词
          await PromptsAPI.createPrompt({
            ...currentPrompt.value,
            tags,
            auto_translate: autoTranslate.value,
          });
        }
        
        // 关闭模态框
        closePromptModal();
        
        // 重新获取数据
        await fetchPrompts();
        await fetchCategories();
      } catch (error) {
        console.error('保存提示词失败', error);
      }
    };
    
    // 确认删除
    const confirmDelete = (prompt: Prompt) => {
      promptToDelete.value = prompt;
      isDeleteModalOpen.value = true;
    };
    
    // 删除提示词
    const deletePrompt = async () => {
      if (!promptToDelete.value) return;
      
      try {
        await PromptsAPI.deletePrompt(promptToDelete.value.id);
        
        // 关闭模态框
        closeDeleteModal();
        
        // 从本地数据中移除
        prompts.value = prompts.value.filter(p => p.id !== promptToDelete.value?.id);
        
        // 重新获取分类
        await fetchCategories();
      } catch (error) {
        console.error('删除提示词失败', error);
      }
    };
    
    // 初始化
    onMounted(async () => {
      await fetchPrompts();
      await fetchCategories();
    });
    
    return {
      prompts,
      categories,
      loading,
      isTranslating,
      searchQuery,
      selectedCategory,
      contentMode,
      quickTranslateInput,
      quickTranslateOutput,
      isQuickTranslating,
      quickTranslateDirection,
      isEditing,
      isPromptModalOpen,
      isDeleteModalOpen,
      promptToDelete,
      currentPrompt,
      tagsInput,
      autoTranslate,
      translatedPreview,
      filteredPrompts,
      fetchPrompts,
      filterByCategory,
      handleSearch,
      toggleFavorite,
      translatePrompt,
      performQuickTranslation,
      copyTranslationToClipboard,
      previewTranslation,
      openCreateModal,
      openEditModal,
      closePromptModal,
      closeDeleteModal,
      savePrompt,
      confirmDelete,
      deletePrompt,
    };
  },
});
</script>

<style scoped>
/* 使用Tailwind实现，无需额外样式 */
</style> 
<template>
  <div class="prompt-library-editor">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
      <!-- 提示词输入区域 -->
      <div class="form-control w-full">
        <label class="label">
          <span class="label-text">提示词</span>
        </label>
        <input 
          type="text" 
          v-model="newPrompt.inputText" 
          class="input input-bordered w-full" 
          placeholder="输入原始提示词文本"
        />
      </div>
      
      <!-- 翻译显示区域 -->
      <div class="form-control w-full">
        <label class="label">
          <span class="label-text">翻译结果</span>
          <span class="text-xs" v-if="isLibTranslating">
            <i class="icon-[tabler--loader-2] animate-spin mr-1"></i> 翻译中...
          </span>
          <span class="text-xs text-primary" v-if="translateDebounceActive">
            <i class="icon-[tabler--clock] animate-pulse mr-1"></i> 准备翻译...
          </span>
        </label>
        <input 
          type="text" 
          v-model="newPrompt.translated" 
          class="input input-bordered w-full" 
          placeholder="自动翻译或手动输入"
        />
      </div>
      
      <!-- 分类选择 -->
      <div class="form-control w-full">
        <label class="label">
          <span class="label-text">一级分类</span>
        </label>
        <div class="flex gap-2">
          <select class="select select-bordered flex-grow" v-model="newPrompt.category">
            <option disabled value="">选择分类</option>
            <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
          </select>
          <button class="btn" @click="showAddCategory = true" v-if="!showAddCategory">
            <i class="icon-[tabler--plus]"></i>
          </button>
        </div>
        <div class="mt-2" v-if="showAddCategory">
          <div class="flex gap-2">
            <input 
              type="text" 
              v-model="newCategory" 
              ref="categoryInput"
              class="input input-bordered flex-grow" 
              placeholder="新分类名称"
              @keyup.enter="addNewCategory"
            />
            <button class="btn btn-primary" @click="addNewCategory">
              <i class="icon-[tabler--check]"></i>
            </button>
            <button class="btn" @click="showAddCategory = false">
              <i class="icon-[tabler--x]"></i>
            </button>
          </div>
        </div>
      </div>
      
      <!-- 二级分类 -->
      <div class="form-control w-full">
        <label class="label">
          <span class="label-text">二级分类</span>
        </label>
        <div class="flex gap-2">
          <select class="select select-bordered flex-grow" v-model="newPrompt.subCategory" :disabled="!newPrompt.category">
            <option disabled value="">选择分类</option>
            <option v-for="subCategory in subCategories" :key="subCategory" :value="subCategory">{{ subCategory }}</option>
          </select>
          <button class="btn" @click="showAddSubCategory = true" v-if="!showAddSubCategory && newPrompt.category">
            <i class="icon-[tabler--plus]"></i>
          </button>
        </div>
        <div class="mt-2" v-if="showAddSubCategory">
          <div class="flex gap-2">
            <input 
              type="text" 
              v-model="newSubCategory" 
              ref="subCategoryInput"
              class="input input-bordered flex-grow" 
              placeholder="新二级分类名称"
              @keyup.enter="addNewSubCategory"
            />
            <button class="btn btn-primary" @click="addNewSubCategory">
              <i class="icon-[tabler--check]"></i>
            </button>
            <button class="btn" @click="showAddSubCategory = false">
              <i class="icon-[tabler--x]"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 操作按钮 -->
    <div class="flex justify-end gap-2">
      <button 
        class="btn btn-primary" 
        @click="saveToLibrary" 
        :disabled="!canSaveToLibrary"
      >
        <i class="icon-[tabler--loader-2] animate-spin mr-1" v-if="isSaving"></i>
        {{ isSaving ? '保存中...' : '保存到提示词库' }}
      </button>
    </div>
    
    <!-- 错误信息 -->
    <div v-if="errorMessage" class="alert alert-error mt-4">
      <i class="icon-[tabler--alert-circle]"></i>
      <span>{{ errorMessage }}</span>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch, onBeforeUnmount } from 'vue';
import { PromptsAPI } from '../api/prompts';
import type { PromptLibraryItem, CreatePromptLibraryItemParams } from '../api/prompts';
import { useDebounce } from '../utils/debounce';

// 提示词数据结构
interface NewPromptData {
  inputText: string;   // 输入文本
  translated: string;  // 翻译结果
  category: string;    // 一级分类
  subCategory: string; // 二级分类
  isEnglish: boolean;  // 是否为英文
}

// 简单的中英文映射字典
const translationMap: Record<string, string> = {
  '写实风格': 'realistic style',
  '动漫风格': 'anime style',
  '水彩画': 'watercolor',
  '油画': 'oil painting',
  '素描': 'sketch',
  '赛博朋克': 'cyberpunk',
  '未来主义': 'futurism',
  '极简主义': 'minimalism',
  '高清': 'high resolution',
  '高质量': 'high quality',
  '细节丰富': 'detailed',
  '精细': 'fine detail',
  // ... 可以保留更多映射
};

export default defineComponent({
  name: 'PromptLibraryEditor',
  
  props: {
    promptLibraryData: {
      type: Array as () => PromptLibraryItem[],
      default: () => []
    },
    selectedPrompt: {
      type: Object as () => PromptLibraryItem | null,
      default: null
    }
  },
  
  emits: ['saved'],
  
  setup(props, { emit }) {
    // 提示词库相关
    const isLibTranslating = ref(false);
    const showAddCategory = ref(false);
    const showAddSubCategory = ref(false);
    const newCategory = ref('');
    const newSubCategory = ref('');
    const isSaving = ref(false);
    const errorMessage = ref('');
    
    // 使用防抖工具
    const translateDebounce = useDebounce(watchNewPromptText, 800);
    
    // 输入框引用
    const categoryInput = ref<HTMLInputElement | null>(null);
    const subCategoryInput = ref<HTMLInputElement | null>(null);
    
    // 监听分类添加状态，自动聚焦
    watch(showAddCategory, (newVal) => {
      if (newVal) {
        // 等待DOM更新后聚焦
        setTimeout(() => {
          categoryInput.value?.focus();
        }, 50);
      }
    });
    
    // 监听二级分类添加状态，自动聚焦
    watch(showAddSubCategory, (newVal) => {
      if (newVal) {
        // 等待DOM更新后聚焦
        setTimeout(() => {
          subCategoryInput.value?.focus();
        }, 50);
      }
    });
    
    // 本地分类管理
    const localCategories = ref<string[]>([]);
    const localSubCategories = ref<{[key: string]: string[]}>({});
    
    // 新提示词数据
    const newPrompt = ref<NewPromptData>({
      inputText: '',
      translated: '',
      category: '',
      subCategory: '',
      isEnglish: false
    });
    
    // 一级分类列表
    const categories = computed(() => {
      // 从props中获取分类
      const categorySet = new Set(props.promptLibraryData.map(item => item.category));
      
      // 添加本地新增的分类
      localCategories.value.forEach(cat => categorySet.add(cat));
      
      return Array.from(categorySet).sort();
    });
    
    // 二级分类列表 (根据选择的一级分类筛选)
    const subCategories = computed(() => {
      let subCategorySet = new Set<string>();
      
      // 如果选择了一级分类，则按该分类筛选
      if (newPrompt.value.category) {
        // 从现有数据中获取二级分类
        const filteredItems = props.promptLibraryData.filter(
          item => item.category === newPrompt.value.category
        );
        filteredItems.forEach(item => {
          if (item.subCategory) subCategorySet.add(item.subCategory);
        });
        
        // 添加本地新增的二级分类
        if (localSubCategories.value[newPrompt.value.category]) {
          localSubCategories.value[newPrompt.value.category].forEach(
            subCat => subCategorySet.add(subCat)
          );
        }
      }
      
      return Array.from(subCategorySet).sort();
    });
    
    // 是否可以保存到提示词库
    const canSaveToLibrary = computed(() => {
      return (
        newPrompt.value.inputText.trim() !== '' && 
        newPrompt.value.translated.trim() !== '' &&
        newPrompt.value.category.trim() !== '' &&
        !isSaving.value
      );
    });
    
    // 重置新提示词表单
    const resetNewPromptForm = () => {
      newPrompt.value = {
        inputText: '',
        translated: '',
        category: '',
        subCategory: '',
        isEnglish: false
      };
      showAddCategory.value = false;
      showAddSubCategory.value = false;
      newCategory.value = '';
      newSubCategory.value = '';
      errorMessage.value = '';
      // 注意：不重置localCategories和localSubCategories，保留用户添加的分类
    };
    
    // 添加新一级分类
    const addNewCategory = () => {
      if (newCategory.value.trim() === '') return;
      
      // 检查是否已存在
      if (categories.value.includes(newCategory.value.trim())) {
        alert('该分类已存在');
        return;
      }
      
      // 添加到本地分类列表
      localCategories.value.push(newCategory.value.trim());
      
      // 设置新分类
      newPrompt.value.category = newCategory.value.trim();
      showAddCategory.value = false;
      newCategory.value = '';
    };
    
    // 添加新二级分类
    const addNewSubCategory = () => {
      if (newSubCategory.value.trim() === '' || !newPrompt.value.category) return;
      
      // 检查是否已存在
      if (subCategories.value.includes(newSubCategory.value.trim())) {
        alert('该二级分类已存在');
        return;
      }
      
      // 确保一级分类在本地子分类映射中存在
      if (!localSubCategories.value[newPrompt.value.category]) {
        localSubCategories.value[newPrompt.value.category] = [];
      }
      
      // 添加到本地二级分类列表
      localSubCategories.value[newPrompt.value.category].push(newSubCategory.value.trim());
      
      // 设置新二级分类
      newPrompt.value.subCategory = newSubCategory.value.trim();
      showAddSubCategory.value = false;
      newSubCategory.value = '';
    };
    
    // 实际执行翻译的方法
    async function watchNewPromptText() {
      const text = newPrompt.value.inputText.trim();
      if (!text) return;
      
      // 检测是否为英文
      const isEnglish = /^[a-zA-Z0-9\s\-_,.]+$/.test(text);
      newPrompt.value.isEnglish = isEnglish;
      
      // 检查本地翻译字典
      if (isEnglish && translationMap[text]) {
        newPrompt.value.translated = translationMap[text];
        return;
      } else if (!isEnglish && translationMap[text]) {
        newPrompt.value.translated = translationMap[text];
        return;
      }
      
      // 检查是否已存在于提示词库中
      const existingPrompt = props.promptLibraryData.find(p => 
        (p.english === text && newPrompt.value.isEnglish) || 
        (p.chinese === text && !newPrompt.value.isEnglish)
      );
      if (existingPrompt) {
        newPrompt.value.translated = newPrompt.value.isEnglish ? existingPrompt.chinese : existingPrompt.english;
        return;
      }
      
      // 调用API翻译
      try {
        isLibTranslating.value = true;
        console.log(`[开始翻译] 文本: "${text}", 方向: ${!isEnglish ? '中->英' : '英->中'}`);
        
        const result = await PromptsAPI.translateText(
          text,
          !isEnglish // 中文->英文 或 英文->中文
        );
        
        if (result && result.translated) {
          newPrompt.value.translated = result.translated;
          console.log(`[翻译成功] 结果: "${result.translated}"`);
        }
      } catch (error) {
        console.error('翻译失败:', error);
        errorMessage.value = '翻译失败，请手动输入翻译';
      } finally {
        isLibTranslating.value = false;
      }
    }
    
    // 监听选中的提示词变化
    watch(() => props.selectedPrompt, (selected) => {
      if (selected) {
        // 判断是否为英文
        const isEnglish = /^[a-zA-Z0-9\s\-_,.]+$/.test(selected.english);
        
        // 如果有选中的提示词，填充到表单
        newPrompt.value = {
          inputText: isEnglish ? selected.english : selected.chinese,
          translated: isEnglish ? selected.chinese : selected.english,
          category: selected.category,
          subCategory: selected.subCategory,
          isEnglish: isEnglish
        };
      }
    }, { immediate: true });
    
    // 保存到提示词库
    const saveToLibrary = async () => {
      if (!canSaveToLibrary.value) return;
      
      try {
        isSaving.value = true;
        errorMessage.value = '';
        
        const newItem: CreatePromptLibraryItemParams = {
          chinese: newPrompt.value.isEnglish ? newPrompt.value.translated : newPrompt.value.inputText,
          english: newPrompt.value.isEnglish ? newPrompt.value.inputText : newPrompt.value.translated,
          category: newPrompt.value.category,
          subCategory: newPrompt.value.subCategory || '默认' // 未选择时使用默认分类
        };
        
        // 如果是在编辑已有提示词，添加ID
        if (props.selectedPrompt) {
          (newItem as any).id = props.selectedPrompt.id;
        }
        
        // 保存到后端
        const savedItem = await PromptsAPI.savePromptToLibrary(newItem);
        
        // 重置表单
        resetNewPromptForm();
        
        // 通知父组件保存成功
        emit('saved', savedItem);
        
        // 显示成功消息
        alert('提示词已成功' + (props.selectedPrompt ? '更新' : '添加') + '到提示词库');
      } catch (error) {
        console.error('保存提示词失败:', error);
        errorMessage.value = '保存提示词失败，请重试';
      } finally {
        isSaving.value = false;
      }
    };
    
    // 组件挂载后初始化
    onMounted(() => {
      // 监听新提示词文本变化
      watch(() => newPrompt.value.inputText, () => {
        if (newPrompt.value.inputText.trim()) {
          translateDebounce.triggerDebounce();
        }
      });
    });
    
    // 组件卸载前清除防抖
    onBeforeUnmount(() => {
      translateDebounce.cancel();
    });
    
    return {
      // 编辑器相关
      newPrompt,
      isLibTranslating,
      isSaving,
      showAddCategory,
      showAddSubCategory,
      newCategory,
      newSubCategory,
      categories,
      subCategories,
      canSaveToLibrary,
      errorMessage,
      localCategories,
      localSubCategories,
      categoryInput,
      subCategoryInput,
      translateDebounceActive: translateDebounce.isActive,
      
      // 方法
      addNewCategory,
      addNewSubCategory,
      saveToLibrary,
    };
  }
});
</script>

<style scoped>
/* 可添加组件特定样式 */
</style> 
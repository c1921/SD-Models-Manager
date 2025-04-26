<template>
  <div class="prompt-badges">
    <!-- 输入区域 -->
    <div class="mb-4">
      <label class="block text-sm font-medium mb-1">提示词输入</label>
      <div class="flex flex-col gap-2">
        <textarea 
          class="textarea textarea-bordered w-full min-h-20" 
          v-model="promptInput"
          @keydown.comma="handleCommaPress"
          placeholder="输入提示词，用逗号（全角、半角均可）分隔，输入后会自动添加到列表" 
        ></textarea>
        <div class="flex justify-between items-center">
          <div class="text-xs text-base-content/70">
            提示：输入的文本会按照逗号（全角、半角均可）自动拆分成多个提示词
            <span v-if="translateTimer !== null" class="ml-2 text-primary animate-pulse">
              <i class="icon-[tabler--transfer] animate-spin mr-1 size-3"></i>准备翻译...
            </span>
            <span v-if="isTranslating" class="ml-2 text-secondary animate-pulse">
              <i class="icon-[tabler--language] animate-spin mr-1 size-3"></i>翻译中...
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 提示词库 -->
    <PromptLibrary 
      :promptLibraryData="promptLibraryData"
      @select-prompt="addPromptFromLibrary" 
    />

    <!-- 已拆分的提示词badges -->
    <div class="mb-4">
      <label class="block text-sm font-medium mb-2">提示词列表</label>
      <div class="bg-base-200 p-3 rounded-md min-h-24">
        <div v-if="prompts.length === 0" class="text-center text-base-content/50 py-6">
          尚未添加任何提示词
        </div>
        <div id="badges-list" v-else class="flex flex-wrap gap-2">
          <div 
            v-for="(prompt, index) in prompts" 
            :key="'prompt-' + index + '-' + prompt.text"
            class="badge badge-lg badge-secondary flex items-center gap-2 px-3 py-2 cursor-move min-w-24 h-auto"
            :class="{ 'opacity-70': prompt.isTranslating }"
            :data-id="index"
          >
            <div class="flex-grow flex flex-col items-center">
              <div class="text-sm w-full text-center" :class="{'translating': prompt.isTranslating && /^[a-zA-Z0-9\s\-_,.]+$/.test(prompt.text)}">
                {{ prompt.chinese }}
                <i v-if="prompt.isTranslating && /^[a-zA-Z0-9\s\-_,.]+$/.test(prompt.text)" class="icon-[tabler--loader-2] animate-spin ml-1 size-3"></i>
              </div>
              <div class="text-xs opacity-80 w-full text-center" :class="{'translating': prompt.isTranslating && !/^[a-zA-Z0-9\s\-_,.]+$/.test(prompt.text)}">
                {{ prompt.english }}
                <i v-if="prompt.isTranslating && !/^[a-zA-Z0-9\s\-_,.]+$/.test(prompt.text)" class="icon-[tabler--loader-2] animate-spin ml-1 size-3"></i>
              </div>
            </div>
            <button 
              class="btn btn-secondary btn-soft btn-xs btn-circle opacity-30 hover:opacity-100 flex-shrink-0"
              @click.stop="removePrompt(index)"
            >
              <i class="icon-[tabler--x] size-3"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 导出按钮 -->
    <div class="flex justify-end gap-2">
      <button class="btn btn-outline" @click="copyToClipboard" :disabled="isTranslating || prompts.length === 0">
        <i class="icon-[tabler--copy] mr-1"></i> 复制
      </button>
      <button class="btn btn-outline" @click="clearAll" :disabled="isTranslating || prompts.length === 0">
        <i class="icon-[tabler--trash] mr-1"></i> 清空
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, nextTick, computed, onBeforeUnmount, watch } from 'vue';
import Sortable from 'sortablejs';
// @ts-ignore
import { PromptsAPI } from '../api/prompts'; // 导入API
import type { PromptLibraryItem } from '../api/prompts'; // 从API文件导入类型
import PromptLibrary from './PromptLibrary.vue'; // 导入提示词库组件
import { useDebounce } from '../utils/debounce'; // 导入防抖工具

// 提示词数据结构
interface PromptData {
  text: string;     // 原始文本
  chinese: string;  // 中文显示
  english: string;  // 英文显示
  isTranslating?: boolean; // 是否正在翻译
}

export default defineComponent({
  name: 'PromptBadges',
  
  components: {
    PromptLibrary
  },
  
  props: {
    promptLibraryData: {
      type: Array as () => PromptLibraryItem[],
      default: () => [],
      required: true
    }
  },
  
  setup(props) {
    // 提示词列表
    const prompts = ref<PromptData[]>([]);
    let sortableInstance: Sortable | null = null;
    let isUpdatingFromTextarea = false; // 标记是否从文本框更新，避免循环
    const rawInputValue = ref(''); // 保存原始输入值，解决末尾逗号问题
    const isTranslating = ref(false); // 全局翻译状态
    
    // 提示词库数据
    const promptLibrary = ref<PromptLibraryItem[]>(props.promptLibraryData);
    
    // 创建批量翻译的防抖函数
    const translateDebounce = useDebounce(async () => {
      console.log('[触发防抖翻译]');
      const needTranslation = prompts.value.filter(p => p.isTranslating);
      if (needTranslation.length > 0) {
        await batchTranslatePrompts(prompts.value);
      }
    }, 1000);
    
    // 监听提示词库数据变化
    watch(() => props.promptLibraryData, (newData) => {
      console.log('[PromptBadges] 提示词库数据更新:', newData.length);
      promptLibrary.value = newData;
      
      // 如果当前有正在编辑的提示词，尝试更新它们的翻译
      if (prompts.value.length > 0) {
        prompts.value.forEach((prompt, index) => {
          // 查找匹配的库中提示词（通过英文或中文匹配）
          const matchingPrompt = newData.find(p => 
            (p.english === prompt.text) || 
            (p.chinese === prompt.text) ||
            (p.english === prompt.english && p.chinese === prompt.chinese)
          );
          
          if (matchingPrompt) {
            // 更新翻译
            prompts.value[index] = {
              ...prompt,
              chinese: matchingPrompt.chinese,
              english: matchingPrompt.english,
              isTranslating: false
            };
          }
        });
      }
    }, { deep: true, immediate: true });
    
    // 计算属性：将提示词转换为文本
    const promptInput = computed({
      get: () => {
        // 如果原始输入值以逗号结尾，保留这个逗号
        if (rawInputValue.value.endsWith(',') || rawInputValue.value.endsWith('，')) {
          return rawInputValue.value;
        }
        
        // 否则返回从提示词列表生成的文本
        if (prompts.value.length === 0) return '';
        return prompts.value.map(p => p.text).join(', ');
      },
      set: (newValue: string) => {
        if (isUpdatingFromTextarea) return;
        
        // 判断是否输入了新的逗号
        const hasNewComma = 
          (rawInputValue.value && !rawInputValue.value.endsWith(',') && !rawInputValue.value.endsWith('，')) && 
          (newValue.endsWith(',') || newValue.endsWith('，'));
        
        isUpdatingFromTextarea = true;
        // 保存原始输入值
        rawInputValue.value = newValue;
        
        // 按逗号（全角和半角）拆分提示词
        const newPromptsText = newValue
          .split(/[,，]/)
          .map(p => p.trim())
          .filter(p => p !== '');
          
        // 将拆分的文本转换为PromptData对象
        const currentTexts = prompts.value.map(p => p.text);
        const newPromptObjects = newPromptsText
          .filter(text => !currentTexts.includes(text)) // 仅处理新添加的提示词
          .map(createPromptData);
          
        // 使用文本匹配现有提示词，保持顺序一致
        const updatedPrompts: PromptData[] = [];
        for (const text of newPromptsText) {
          // 查找现有的提示词
          const existingPrompt = prompts.value.find(p => p.text === text);
          if (existingPrompt) {
            updatedPrompts.push(existingPrompt);
          } else {
            // 查找新创建的提示词
            const newPrompt = newPromptObjects.find(p => p.text === text);
            if (newPrompt) {
              updatedPrompts.push(newPrompt);
            }
          }
        }
        
        // 更新提示词列表
        prompts.value = updatedPrompts;
        
        console.log('[输入更新] 文本:', newValue);
        console.log('[输入更新] 解析结果:', updatedPrompts);
        
        nextTick(() => {
          initSortable();
          isUpdatingFromTextarea = false;
          
          // 如果输入了新的逗号并且有需要翻译的提示词，则触发防抖翻译
          if (hasNewComma) {
            const needTranslation = updatedPrompts.filter(p => p.isTranslating);
            if (needTranslation.length > 0) {
              console.log('[检测到逗号，准备翻译]', needTranslation);
              debounceTranslate();
            }
          }
        });
      }
    });
    
    // 防抖翻译函数
    const debounceTranslate = () => {
      translateDebounce.triggerDebounce();
    };
    
    // 创建提示词对象
    const createPromptData = (text: string): PromptData => {
      // 检查是否是英文
      const isEnglish = /^[a-zA-Z0-9\s\-_,.]+$/.test(text);
      
      console.log(`[创建提示词] 文本: "${text}", 是否英文: ${isEnglish}`);
      
      // 初始创建提示词对象
      const promptData: PromptData = {
        text: text,
        chinese: isEnglish ? '翻译中...' : text,
        english: isEnglish ? text : '翻译中...',
        isTranslating: true
      };
      
      // 查找提示词库中是否已有该提示词的翻译
      const existingPrompt = promptLibrary.value.find(p => 
        (isEnglish && p.english === text) || (!isEnglish && p.chinese === text)
      );
      
      if (existingPrompt) {
        promptData.chinese = existingPrompt.chinese;
        promptData.english = existingPrompt.english;
        promptData.isTranslating = false;
        console.log(`[库中查找] 文本: "${text}", 找到翻译: "${isEnglish ? existingPrompt.chinese : existingPrompt.english}"`);
      } else {
        console.log(`[需要翻译] 文本: "${text}", 当前状态:`, promptData);
      }
      
      return promptData;
    };
    

    // 批量翻译提示词
    const batchTranslatePrompts = async (promptsToTranslate: PromptData[]) => {
      if (promptsToTranslate.length === 0) return;
      
      console.log('[开始批量翻译]', {
        总数: promptsToTranslate.length,
        待翻译: promptsToTranslate.filter(p => p.isTranslating).length
      });
      
      const chinesePrompts: { text: string, index: number }[] = [];
      const englishPrompts: { text: string, index: number }[] = [];
      
      // 分类需要翻译的提示词
      promptsToTranslate.forEach((prompt, index) => {
        if (prompt.isTranslating) {
          const isEnglish = /^[a-zA-Z0-9\s\-_,.]+$/.test(prompt.text);
          if (isEnglish) {
            englishPrompts.push({ text: prompt.text, index });
          } else {
            chinesePrompts.push({ text: prompt.text, index });
          }
        }
      });
      
      console.log('[翻译分类]', {
        英文数量: englishPrompts.length,
        中文数量: chinesePrompts.length
      });
      
      isTranslating.value = true;
      
      try {
        // 英文到中文的批量翻译
        if (englishPrompts.length > 0) {
          console.log('[开始英->中翻译]', englishPrompts.map(p => p.text));
          const textsToTranslate = englishPrompts.map(item => item.text);
          const results = await PromptsAPI.batchTranslate(textsToTranslate, false);
          
          console.log('[英->中翻译结果]', results);
          
          results.forEach((result, i) => {
            const index = englishPrompts[i].index;
            prompts.value[index].chinese = result.translated;
            prompts.value[index].isTranslating = false;
          });
        }
        
        // 中文到英文的批量翻译
        if (chinesePrompts.length > 0) {
          console.log('[开始中->英翻译]', chinesePrompts.map(p => p.text));
          const textsToTranslate = chinesePrompts.map(item => item.text);
          const results = await PromptsAPI.batchTranslate(textsToTranslate, true);
          
          console.log('[中->英翻译结果]', results);
          
          results.forEach((result, i) => {
            const index = chinesePrompts[i].index;
            prompts.value[index].english = result.translated;
            prompts.value[index].isTranslating = false;
          });
        }
      } catch (error) {
        console.error('[批量翻译失败]', error);
        // 标记翻译失败
        [...englishPrompts, ...chinesePrompts].forEach(item => {
          const isEnglish = /^[a-zA-Z0-9\s\-_,.]+$/.test(prompts.value[item.index].text);
          if (isEnglish) {
            prompts.value[item.index].chinese = '翻译失败';
          } else {
            prompts.value[item.index].english = '翻译失败';
          }
          prompts.value[item.index].isTranslating = false;
        });
      } finally {
        console.log('[批量翻译完成]', {
          总数: promptsToTranslate.length,
          剩余未翻译: prompts.value.filter(p => p.isTranslating).length
        });
        isTranslating.value = false;
      }
    };
    
    // 移除提示词
    const removePrompt = (index: number) => {
      prompts.value.splice(index, 1);
      
      // 更新输入框，但不触发计算属性的set方法
      isUpdatingFromTextarea = true;
      rawInputValue.value = prompts.value.map(p => p.text).join(', ');
      setTimeout(() => {
        isUpdatingFromTextarea = false;
      }, 0);
    };
    
    // 从提示词库添加提示词
    const addPromptFromLibrary = (libraryItem: PromptLibraryItem) => {
      // 检查是否已存在
      const exists = prompts.value.some(p => 
        (p.chinese === libraryItem.chinese && p.english === libraryItem.english)
      );
      if (exists) {
        return; // 已存在则不添加
      }
      
      // 创建新提示词对象
      const newPromptData: PromptData = {
        text: libraryItem.english, // 使用英文作为text字段
        chinese: libraryItem.chinese,
        english: libraryItem.english,
        isTranslating: false // 直接使用库中的翻译，不需要翻译
      };
      
      // 添加到提示词列表
      prompts.value.push(newPromptData);
      
      // 更新输入框
      isUpdatingFromTextarea = true;
      rawInputValue.value = prompts.value.map(p => p.text).join(', ');
      setTimeout(() => {
        isUpdatingFromTextarea = false;
      }, 0);
      
      // 重新初始化拖拽排序
      nextTick(() => {
        initSortable();
      });
    };
    
    // 初始化Sortable.js
    const initSortable = () => {
      const badgesList = document.querySelector('#badges-list') as HTMLElement;
      if (!badgesList) return;
      
      // 销毁之前的实例
      if (sortableInstance) {
        sortableInstance.destroy();
      }
      
      // 创建新的实例
      sortableInstance = Sortable.create(badgesList, {
        animation: 150,
        ghostClass: 'opacity-60',
        dragClass: '!border-0',
        handle: '.badge',
        onUpdate: (evt) => {
          // 更新数组顺序
          const oldIndex = evt.oldIndex!;
          const newIndex = evt.newIndex!;
          
          // 只有当位置真的变化时才更新
          if (oldIndex !== newIndex) {
            const temp = [...prompts.value];
            const movedItem = temp.splice(oldIndex, 1)[0];
            temp.splice(newIndex, 0, movedItem);
            prompts.value = temp;
            
            // 同步更新输入框，但不触发计算属性的set方法
            isUpdatingFromTextarea = true;
            rawInputValue.value = prompts.value.map(p => p.text).join(', ');
            console.log('[拖拽排序] 同步更新输入框:', rawInputValue.value);
            setTimeout(() => {
              isUpdatingFromTextarea = false;
            }, 0);
          }
        }
      });
    };
    
    // 复制到剪贴板
    const copyToClipboard = () => {
      if (prompts.value.length === 0) return;
      
      // 检查是否有正在翻译的提示词
      const hasTranslating = prompts.value.some(p => p.isTranslating);
      if (hasTranslating) {
        if (!confirm('有部分提示词正在翻译中，是否继续复制？')) {
          return;
        }
      }
      
      // 获取英文提示词并拼接，始终使用半角逗号加空格
      const text = prompts.value.map(p => {
        // 使用英文，如果正在翻译中则使用原始文本
        return p.isTranslating ? 
          (/^[a-zA-Z0-9\s\-_,.]+$/.test(p.text) ? p.text : '翻译中...') : 
          p.english;
      }).join(', ');
      
      navigator.clipboard.writeText(text)
        .then(() => {
          alert('已复制到剪贴板');
        })
        .catch(err => {
          console.error('复制失败:', err);
        });
    };
    
    // 清空所有提示词
    const clearAll = () => {
      if (prompts.value.length === 0) return;
      
      if (confirm('确认清空所有提示词？')) {
        prompts.value = [];
        
        // 更新输入框，但不触发计算属性的set方法
        isUpdatingFromTextarea = true;
        rawInputValue.value = '';
        setTimeout(() => {
          isUpdatingFromTextarea = false;
        }, 0);
      }
    };
    
    // 处理逗号按键
    const handleCommaPress = () => {
      console.log('[检测到逗号按键]');
      // 延迟处理，确保v-model更新
      setTimeout(() => {
        const needTranslation = prompts.value.filter(p => p.isTranslating);
        if (needTranslation.length > 0) {
          debounceTranslate();
        }
      }, 10);
    };
    
    // 从提示词库中查找匹配的提示词
    const findMatchingPrompts = (text: string) => {
      return promptLibrary.value.filter(item => {
        const regex = new RegExp(`\\b${text}\\b`, 'i');
        return regex.test(item.english) || regex.test(item.chinese);
      });
    };
    
    // 组件挂载后初始化
    onMounted(() => {
      // 初始化拖拽排序
      nextTick(() => {
        if (prompts.value.length > 0) {
          initSortable();
        }
      });
    });
    
    // 组件卸载前清除定时器
    onBeforeUnmount(() => {
      translateDebounce.cancel();
    });
    
    return {
      promptInput,
      prompts,
      removePrompt,
      copyToClipboard,
      clearAll,
      isTranslating,
      handleCommaPress,
      translateTimer: translateDebounce.isActive,
      addPromptFromLibrary,
      findMatchingPrompts
    };
  }
});
</script>

<style scoped>
.badge {
  position: relative;
  justify-content: space-between;
  text-align: center;
  word-break: break-word;
  overflow: visible;
  height: auto !important;
  white-space: normal;
}

.translating {
  font-style: italic;
  opacity: 0.7;
}
</style> 
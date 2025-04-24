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
    <PromptLibrary @select-prompt="addPromptFromLibrary" />

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
            class="badge badge-lg badge-primary flex items-center gap-2 px-3 py-2 cursor-move min-w-24 h-auto"
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
              class="btn btn-ghost btn-xs btn-circle flex-shrink-0"
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
import { PromptsAPI } from '../api/prompts'; // 导入API
import type { PromptLibraryItem } from '../api/prompts'; // 从API文件导入类型
import PromptLibrary from './PromptLibrary.vue'; // 导入提示词库组件

// 提示词数据结构
interface PromptData {
  text: string;     // 原始文本
  chinese: string;  // 中文显示
  english: string;  // 英文显示
  isTranslating?: boolean; // 是否正在翻译
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
  '夜景': 'night scene',
  '黎明': 'dawn',
  '黄昏': 'dusk',
  '雨天': 'rainy',
  '雪景': 'snow scene',
  '海边': 'seaside',
  '森林': 'forest',
  '城市': 'city',
  '星空': 'starry sky',
  '广角镜头': 'wide-angle lens',
  '长焦镜头': 'telephoto lens',
  '鱼眼镜头': 'fisheye lens',
  '微距': 'macro',
  '景深': 'depth of field',
  '散景': 'bokeh',
  '低角度': 'low angle',
  '航拍': 'aerial photography',
  '逆光': 'backlight',
  '侧光': 'sidelight',
  '柔光': 'soft light',
  '硬光': 'hard light',
  '聚光': 'spotlight',
  '霓虹灯': 'neon lights',
  '金色光芒': 'golden rays',
  '蓝色调': 'blue tone'
};

export default defineComponent({
  name: 'PromptBadges',
  
  components: {
    PromptLibrary
  },
  
  setup() {
    // 提示词列表
    const prompts = ref<PromptData[]>([]);
    let sortableInstance: Sortable | null = null;
    let isUpdatingFromTextarea = false; // 标记是否从文本框更新，避免循环
    const rawInputValue = ref(''); // 保存原始输入值，解决末尾逗号问题
    const isTranslating = ref(false); // 全局翻译状态
    let translateTimer: number | null = null; // 翻译防抖定时器
    
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
      // 清除之前的定时器
      if (translateTimer !== null) {
        clearTimeout(translateTimer);
      }
      
      // 设置新的定时器
      translateTimer = window.setTimeout(() => {
        console.log('[触发防抖翻译]');
        const needTranslation = prompts.value.filter(p => p.isTranslating);
        if (needTranslation.length > 0) {
          batchTranslatePrompts(prompts.value);
        }
        translateTimer = null;
      }, 1000); // 1秒防抖延迟
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
      
      // 使用已有翻译
      if (isEnglish && translationMap[text]) {
        promptData.chinese = translationMap[text];
        promptData.isTranslating = false;
        console.log(`[本地翻译] 英->中: "${text}" -> "${translationMap[text]}"`);
      } else if (!isEnglish && translationMap[text]) {
        promptData.english = translationMap[text];
        promptData.isTranslating = false;
        console.log(`[本地翻译] 中->英: "${text}" -> "${translationMap[text]}"`);
      } else {
        console.log(`[需要翻译] 文本: "${text}", 当前状态:`, promptData);
      }
      
      return promptData;
    };
    
    // 翻译单个提示词
    const translatePrompt = async (prompt: PromptData, index: number) => {
      if (!prompt.isTranslating) return prompt;
      
      const isEnglish = /^[a-zA-Z0-9\s\-_,.]+$/.test(prompt.text);
      console.log(`[开始翻译] 索引: ${index}, 文本: "${prompt.text}", 方向: ${isEnglish ? '英->中' : '中->英'}`);
      
      try {
        const result = await PromptsAPI.translateText(
          prompt.text,
          !isEnglish // 中文->英文 或 英文->中文
        );
        
        if (result && result.translated) {
          if (isEnglish) {
            prompt.chinese = result.translated;
          } else {
            prompt.english = result.translated;
          }
          prompt.isTranslating = false;
          
          console.log(`[翻译成功] 文本: "${prompt.text}" -> "${result.translated}"`);
          
          // 更新提示词列表中的数据
          const updatedPrompts = [...prompts.value];
          updatedPrompts[index] = prompt;
          prompts.value = updatedPrompts;
        }
      } catch (error) {
        console.error(`[翻译失败] 文本: "${prompt.text}", 错误:`, error);
        if (/^[a-zA-Z0-9\s\-_,.]+$/.test(prompt.text)) {
          prompt.chinese = '翻译失败';
        } else {
          prompt.english = '翻译失败';
        }
        prompt.isTranslating = false;
      }
      
      return prompt;
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
      const exists = prompts.value.some(p => p.text === libraryItem.text);
      if (exists) {
        return; // 已存在则不添加
      }
      
      // 创建新提示词对象
      const newPromptData: PromptData = {
        text: libraryItem.text,
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
      if (translateTimer !== null) {
        clearTimeout(translateTimer);
        translateTimer = null;
      }
    });
    
    return {
      promptInput,
      prompts,
      removePrompt,
      copyToClipboard,
      clearAll,
      isTranslating,
      handleCommaPress,
      translateTimer,
      addPromptFromLibrary
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
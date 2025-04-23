<template>
  <div class="prompt-badges">
    <!-- 输入区域 -->
    <div class="mb-4">
      <label class="block text-sm font-medium mb-1">提示词输入</label>
      <div class="flex gap-2">
        <input 
          type="text" 
          class="input input-bordered flex-grow" 
          v-model="promptInput"
          @keydown.enter="addPrompt"
          placeholder="输入提示词，按回车或点击添加按钮拆分显示" 
        />
        <button class="btn btn-primary" @click="addPrompt">添加</button>
      </div>
      <div class="text-xs text-base-content/70 mt-1">
        提示：输入的文本会按照逗号、空格等分隔符自动拆分
      </div>
    </div>

    <!-- 分隔符选择 -->
    <div class="mb-4">
      <label class="block text-sm font-medium mb-1">分隔符选择</label>
      <div class="join">
        <button 
          class="join-item btn btn-sm" 
          :class="separator === ',' ? 'btn-active' : ''"
          @click="setSeparator(',')"
        >
          逗号 (,)
        </button>
        <button 
          class="join-item btn btn-sm" 
          :class="separator === ' ' ? 'btn-active' : ''"
          @click="setSeparator(' ')"
        >
          空格
        </button>
        <button 
          class="join-item btn btn-sm" 
          :class="separator === '\n' ? 'btn-active' : ''"
          @click="setSeparator('\n')"
        >
          换行
        </button>
      </div>
    </div>

    <!-- 颜色选择 -->
    <div class="mb-4">
      <label class="block text-sm font-medium mb-1">Badge 颜色</label>
      <div class="join">
        <button 
          class="join-item btn btn-sm" 
          :class="badgeColor === 'badge-primary' ? 'btn-active' : ''"
          @click="setBadgeColor('badge-primary')"
        >
          主色
        </button>
        <button 
          class="join-item btn btn-sm" 
          :class="badgeColor === 'badge-secondary' ? 'btn-active' : ''"
          @click="setBadgeColor('badge-secondary')"
        >
          次色
        </button>
        <button 
          class="join-item btn btn-sm" 
          :class="badgeColor === 'badge-accent' ? 'btn-active' : ''"
          @click="setBadgeColor('badge-accent')"
        >
          强调
        </button>
        <button 
          class="join-item btn btn-sm" 
          :class="badgeColor === 'badge-neutral' ? 'btn-active' : ''"
          @click="setBadgeColor('badge-neutral')"
        >
          中性
        </button>
      </div>
    </div>

    <!-- 示例提示词 -->
    <div class="mb-4">
      <label class="block text-sm font-medium mb-2">示例提示词</label>
      <div class="flex flex-wrap gap-2">
        <button 
          v-for="(category, index) in exampleCategories" 
          :key="index"
          class="btn btn-sm btn-outline"
          @click="loadExamplePrompts(category.id)"
        >
          {{ category.name }}
        </button>
      </div>
    </div>

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
            class="badge badge-lg flex items-center gap-2 px-3 py-2 cursor-move min-w-24 h-auto"
            :class="badgeColor"
            :data-id="index"
          >
            <div class="flex-grow flex flex-col items-center">
              <div class="text-sm w-full text-center">{{ prompt.chinese }}</div>
              <div class="text-xs opacity-80 w-full text-center">{{ prompt.english }}</div>
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
      <button class="btn btn-outline" @click="copyToClipboard">
        <i class="icon-[tabler--copy] mr-1"></i> 复制
      </button>
      <button class="btn btn-outline" @click="clearAll">
        <i class="icon-[tabler--trash] mr-1"></i> 清空
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, nextTick } from 'vue';
import Sortable from 'sortablejs';

// 提示词数据结构
interface PromptData {
  text: string;     // 原始文本
  chinese: string;  // 中文显示
  english: string;  // 英文显示
}

// 示例提示词数据
interface ExampleCategory {
  id: string;
  name: string;
  prompts: string[];
}

// 各类示例提示词
const examplePromptsData: Record<string, ExampleCategory> = {
  style: {
    id: 'style',
    name: '风格类',
    prompts: ['写实风格', '动漫风格', '水彩画', '油画', '素描', '赛博朋克', '未来主义', '极简主义']
  },
  quality: {
    id: 'quality',
    name: '质量类',
    prompts: ['高清', '8K', '高质量', '细节丰富', '精细', 'masterpiece', 'best quality', 'ultra detailed']
  },
  scene: {
    id: 'scene',
    name: '场景类',
    prompts: ['夜景', '黎明', '黄昏', '雨天', '雪景', '海边', '森林', '城市', '星空']
  },
  camera: {
    id: 'camera',
    name: '相机参数',
    prompts: ['广角镜头', '长焦镜头', '鱼眼镜头', '微距', '景深', '散景', '低角度', '航拍']
  },
  lighting: {
    id: 'lighting',
    name: '光照类',
    prompts: ['逆光', '侧光', '柔光', '硬光', '聚光', '霓虹灯', '金色光芒', '蓝色调']
  }
};

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
  
  setup() {
    const promptInput = ref('');
    const prompts = ref<PromptData[]>([]);
    const separator = ref(',');
    const badgeColor = ref('badge-primary');
    const exampleCategories = ref<ExampleCategory[]>(Object.values(examplePromptsData));
    let sortableInstance: Sortable | null = null;
    
    // 创建提示词对象
    const createPromptData = (text: string): PromptData => {
      // 检查是否是英文
      const isEnglish = /^[a-zA-Z0-9\s\-_,.]+$/.test(text);
      
      // 如果是英文文本
      if (isEnglish) {
        // 这里可以添加英译中的逻辑，目前简单处理
        return {
          text: text,
          english: text,
          chinese: '翻译中...' // 实际应用中可以接入翻译API
        };
      } 
      // 如果是中文文本
      else {
        return {
          text: text,
          chinese: text,
          english: translationMap[text] || text // 尝试从字典获取翻译，没有则使用原文
        };
      }
    };
    
    // 添加提示词
    const addPrompt = () => {
      if (!promptInput.value.trim()) return;
      
      // 按分隔符拆分提示词
      const newPrompts = promptInput.value
        .split(separator.value)
        .map(p => p.trim())
        .filter(p => p !== '')
        .map(createPromptData);
      
      // 添加到提示词列表
      prompts.value = [...prompts.value, ...newPrompts];
      
      // 清空输入框
      promptInput.value = '';
      
      // 重新初始化拖拽排序
      nextTick(() => {
        initSortable();
      });
    };
    
    // 移除提示词
    const removePrompt = (index: number) => {
      prompts.value.splice(index, 1);
    };
    
    // 设置分隔符
    const setSeparator = (sep: string) => {
      separator.value = sep;
    };
    
    // 设置badge颜色
    const setBadgeColor = (color: string) => {
      badgeColor.value = color;
    };
    
    // 加载示例提示词
    const loadExamplePrompts = (categoryId: string) => {
      const category = examplePromptsData[categoryId];
      if (category) {
        // 将字符串转换为PromptData对象
        const promptDataList = category.prompts.map(createPromptData);
        
        // 如果已有提示词，询问是否替换
        if (prompts.value.length > 0) {
          if (confirm('是否要替换当前的提示词列表？点击确定替换，点击取消则添加到现有列表')) {
            prompts.value = [...promptDataList];
          } else {
            prompts.value = [...prompts.value, ...promptDataList];
          }
        } else {
          prompts.value = [...promptDataList];
        }
        
        // 重新初始化拖拽排序
        nextTick(() => {
          initSortable();
        });
      }
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
          }
        }
      });
    };
    
    // 复制到剪贴板
    const copyToClipboard = () => {
      if (prompts.value.length === 0) return;
      
      // 获取英文提示词并拼接
      const text = prompts.value.map(p => p.english).join(', ');
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
      }
    };
    
    // 组件挂载后初始化Sortable.js
    onMounted(() => {
      nextTick(() => {
        if (prompts.value.length > 0) {
          initSortable();
        }
      });
    });
    
    return {
      promptInput,
      prompts,
      separator,
      badgeColor,
      exampleCategories,
      addPrompt,
      removePrompt,
      setSeparator,
      setBadgeColor,
      loadExamplePrompts,
      copyToClipboard,
      clearAll
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
</style> 
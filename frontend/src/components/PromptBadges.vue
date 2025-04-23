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
            :key="'prompt-' + index + '-' + prompt"
            class="badge badge-lg flex items-center gap-1 cursor-move"
            :class="badgeColor"
            :data-id="index"
          >
            {{ prompt }}
            <button 
              class="btn btn-ghost btn-xs btn-circle"
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

export default defineComponent({
  name: 'PromptBadges',
  
  setup() {
    const promptInput = ref('');
    const prompts = ref<string[]>([]);
    const separator = ref(',');
    const badgeColor = ref('badge-primary');
    const exampleCategories = ref<ExampleCategory[]>(Object.values(examplePromptsData));
    let sortableInstance: Sortable | null = null;
    
    // 添加提示词
    const addPrompt = () => {
      if (!promptInput.value.trim()) return;
      
      // 按分隔符拆分提示词
      const newPrompts = promptInput.value
        .split(separator.value)
        .map(p => p.trim())
        .filter(p => p !== '');
      
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
        // 如果已有提示词，询问是否替换
        if (prompts.value.length > 0) {
          if (confirm('是否要替换当前的提示词列表？点击确定替换，点击取消则添加到现有列表')) {
            prompts.value = [...category.prompts];
          } else {
            prompts.value = [...prompts.value, ...category.prompts];
          }
        } else {
          prompts.value = [...category.prompts];
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
      
      const text = prompts.value.join(', ');
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
<template>
  <!-- 桌面版筛选器侧边栏 -->
  <div 
    v-if="modelCount > 0" 
    class="hidden lg:block w-80 border-l border-base-200 h-full overflow-hidden bg-base-100"
  >
    <div class="h-full overflow-y-auto px-6 py-4">
      <div class="mb-3 border-b border-base-200 pb-3">
        <span class="text-lg font-medium text-base-content">筛选器</span>
      </div>
      <!-- 筛选器容器 -->
      <div>
        <div v-for="(filter, key) in filters" :key="key" class="mb-6">
          <h6 class="text-base font-medium mb-2 text-base-content">{{ filter.label }}</h6>
          <div class="space-y-2">
            <div v-for="option in filter.options" :key="option.value" class="flex items-center gap-2">
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                :id="`filter-${key}-${option.value}`"
                :value="option.value"
                v-model="filter.selected"
              />
              <label class="label-text text-base text-base-content/80" :for="`filter-${key}-${option.value}`">
                {{ option.label }} ({{ option.count }})
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 移动端筛选器抽屉触发器（隐藏） -->
  <button 
    ref="filterSidebarTrigger" 
    type="button" 
    class="hidden" 
    aria-haspopup="dialog" 
    aria-expanded="false" 
    aria-controls="filter-sidebar" 
    data-overlay="#filter-sidebar"
  ></button>

  <!-- 移动端筛选器抽屉 -->
  <aside 
    id="filter-sidebar" 
    class="overlay overlay-open:translate-x-0 drawer drawer-end max-w-72 hidden" 
    role="dialog" 
    aria-modal="true" 
    tabindex="-1"
  >
    <div class="drawer-dialog">
      <div class="drawer-content bg-base-100">
        <div class="drawer-header border-b border-base-200">
          <h5 class="drawer-title text-base-content">筛选器</h5>
          <button 
            type="button" 
            class="btn btn-text btn-circle btn-sm" 
            aria-label="关闭" 
            data-overlay="#filter-sidebar"
          >
            <span class="icon-[tabler--x] size-5"></span>
          </button>
        </div>
        <div class="drawer-body">
          <div v-for="(filter, key) in filters" :key="`mobile-${key}`" class="mb-6">
            <h6 class="text-base font-medium mb-2 text-base-content">{{ filter.label }}</h6>
            <div class="space-y-2">
              <div v-for="option in filter.options" :key="`mobile-${option.value}`" class="flex items-center gap-2">
                <input 
                  type="checkbox" 
                  class="checkbox checkbox-primary" 
                  :id="`mobile-filter-${key}-${option.value}`"
                  :value="option.value"
                  v-model="filter.selected"
                />
                <label class="label-text text-base text-base-content/80" :for="`mobile-filter-${key}-${option.value}`">
                  {{ option.label }} ({{ option.count }})
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// 类型定义
interface FilterOption {
  label: string;
  value: string;
  count: number;
}

interface Filter {
  label: string;
  options: FilterOption[];
  selected: string[];
}

defineProps<{
  filters: Record<string, Filter>;
  modelCount: number;
}>();

// 移动端筛选器抽屉触发元素
const filterSidebarTrigger = ref<HTMLButtonElement | null>(null);

// 打开筛选器侧边栏
function openFilterSidebar() {
  if (filterSidebarTrigger.value) {
    filterSidebarTrigger.value.click();
  }
}

// 向父组件暴露方法
defineExpose({
  openFilterSidebar
});
</script> 
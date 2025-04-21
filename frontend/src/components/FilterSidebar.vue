<template>
  <!-- 桌面版筛选器侧边栏 -->
  <div 
    v-if="modelCount > 0" 
    class="hidden lg:block w-1/4 border-l border-gray-200 dark:border-gray-700 pl-6 bg-gray-50 dark:bg-gray-800"
  >
    <div class="sticky top-20 h-[calc(100vh-5rem)] overflow-y-auto">
      <div class="pb-3 mb-3 border-b border-gray-200 dark:border-gray-700">
        <span class="text-lg font-medium">筛选器</span>
      </div>
      <!-- 筛选器容器 -->
      <div>
        <div v-for="(filter, key) in filters" :key="key" class="mb-6">
          <h6 class="text-base font-medium mb-2">{{ filter.label }}</h6>
          <div class="space-y-2">
            <div v-for="option in filter.options" :key="option.value" class="flex items-center gap-2">
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                :id="`filter-${key}-${option.value}`"
                :value="option.value"
                v-model="filter.selected"
              />
              <label class="label-text text-base" :for="`filter-${key}-${option.value}`">
                {{ option.label }} ({{ option.count }})
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 移动端筛选器抽屉 -->
  <button 
    ref="filterSidebarTrigger" 
    type="button" 
    class="hidden" 
    aria-controls="filter-sidebar" 
    data-drawer="#filter-sidebar"
  ></button>

  <div 
    id="filter-sidebar" 
    class="drawer drawer-end"
    role="dialog" 
    aria-modal="true" 
    tabindex="-1"
  >
    <div class="drawer-dialog">
      <div class="drawer-content">
        <div class="drawer-header">
          <h5 class="drawer-title">筛选器</h5>
          <button 
            type="button" 
            class="btn btn-text btn-circle btn-sm" 
            aria-label="关闭" 
            data-drawer="#filter-sidebar"
          >
            <span class="icon-[tabler--x] size-4"></span>
          </button>
        </div>
        <div class="drawer-body">
          <div v-for="(filter, key) in filters" :key="`mobile-${key}`" class="mb-6">
            <h6 class="text-base font-medium mb-2">{{ filter.label }}</h6>
            <div class="space-y-2">
              <div v-for="option in filter.options" :key="`mobile-${option.value}`" class="flex items-center gap-2">
                <input 
                  type="checkbox" 
                  class="checkbox checkbox-primary" 
                  :id="`mobile-filter-${key}-${option.value}`"
                  :value="option.value"
                  v-model="filter.selected"
                />
                <label class="label-text text-base" :for="`mobile-filter-${key}-${option.value}`">
                  {{ option.label }} ({{ option.count }})
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineExpose } from 'vue';

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
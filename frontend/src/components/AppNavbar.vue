<template>
  <!-- 导航栏 -->
  <nav class="sticky top-0 z-10 shadow bg-base-100">
    <div class="container mx-auto px-1 flex items-center justify-between h-16">
      <a href="#" class="flex items-center">
        <img src="/favicon.svg" alt="Stable Diffusion 模型管理器" class="h-7">
      </a>
      
      <div class="flex items-center gap-2">
        <button 
          type="button"
          :class="nsfw ? 'btn btn-error' : 'btn btn-outline'"
          title="NSFW内容控制"
          @click="toggleNsfw"
        >
          <span class="icon-[tabler--eye-off] size-5 me-2" v-if="!nsfw"></span>
          <span class="icon-[tabler--eye] size-5 me-2" v-else></span>
          <span>NSFW {{ nsfw ? '已开启' : '已关闭' }}</span>
        </button>

        <button 
          type="button"
          :class="blurNsfw ? 'btn btn-outline btn-neutral' : 'btn btn-outline btn-error'" 
          title="NSFW图片模糊控制"
          @click="toggleBlurNsfw"
        >
          <span class="icon-[tabler--blur] size-5 me-1.5" v-if="blurNsfw"></span>
          <span class="icon-[tabler--blur-off] size-5 me-1.5" v-else></span>
          <span>模糊{{ blurNsfw ? '开' : '关' }}</span>
        </button>

        <div class="w-3"></div>

        <button 
          type="button"
          class="btn btn-icon btn-outline btn-neutral"
          title="设置"
          @click="onOpenSettings"
        >
          <span class="icon-[tabler--settings] size-5"></span>
        </button>

        <button 
          type="button"
          class="btn btn-icon btn-outline btn-neutral"
          title="切换主题"
          @click="toggleDarkMode"
        >
          <span class="icon-[tabler--sun] size-5" v-if="!darkMode"></span>
          <span class="icon-[tabler--moon] size-5" v-else></span>
        </button>
        
        <button 
          type="button"
          class="btn btn-icon btn-outline btn-accent lg:hidden"
          title="筛选器"
          @click="onOpenFilterSidebar"
        >
          <span class="icon-[tabler--filter] size-5"></span>
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
defineProps<{
  nsfw: boolean;
  darkMode: boolean;
  blurNsfw: boolean;
}>();

const emit = defineEmits<{
  'toggle-nsfw': [];
  'toggle-blur-nsfw': [];
  'toggle-dark-mode': [];
  'open-settings': [];
  'open-filter-sidebar': [];
}>();

function toggleNsfw() {
  emit('toggle-nsfw');
}

function toggleBlurNsfw() {
  emit('toggle-blur-nsfw');
}

function toggleDarkMode() {
  emit('toggle-dark-mode');
}

function onOpenSettings() {
  emit('open-settings');
}

function onOpenFilterSidebar() {
  emit('open-filter-sidebar');
}
</script> 
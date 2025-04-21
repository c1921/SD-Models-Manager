<template>
  <!-- 导航栏 -->
  <nav class="sticky top-0 z-10 bg-white dark:bg-gray-800 shadow">
    <div class="container mx-auto px-4 flex items-center justify-between h-16">
      <a href="#" class="flex items-center">
        <img src="/favicon.svg" alt="Stable Diffusion 模型管理器" class="h-7">
      </a>
      
      <div class="flex items-center space-x-3">
        <button 
          type="button"
          class="btn" 
          :class="nsfw ? 'btn-primary' : 'btn-outline-primary'"
          @click="toggleNsfw"
        >
          <span 
            class="inline-block me-1.5 size-4"
            :class="nsfw ? 'icon-[tabler--eye]' : 'icon-[tabler--eye-off]'"
          ></span>
          <span>NSFW {{ nsfw ? '已开启' : '已关闭' }}</span>
        </button>

        <button 
          type="button"
          class="btn btn-icon btn-ghost"
          @click="onOpenSettings"
        >
          <span class="icon-[tabler--settings] size-5"></span>
        </button>

        <button 
          type="button"
          class="btn btn-icon btn-ghost"
          @click="toggleDarkMode"
        >
          <span 
            class="size-5"
            :class="darkMode ? 'icon-[tabler--moon]' : 'icon-[tabler--sun]'"
          ></span>
        </button>
        
        <button 
          type="button"
          class="btn btn-icon btn-ghost lg:hidden"
          @click="onOpenFilterSidebar"
        >
          <span class="icon-[tabler--filter] size-5"></span>
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';

defineProps<{
  nsfw: boolean;
  darkMode: boolean;
}>();

const emit = defineEmits<{
  'toggle-nsfw': [];
  'toggle-dark-mode': [];
  'open-settings': [];
  'open-filter-sidebar': [];
}>();

function toggleNsfw() {
  emit('toggle-nsfw');
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
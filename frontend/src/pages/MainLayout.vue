<template>
  <div class="min-h-screen h-screen flex flex-col overflow-hidden">
    <!-- 主导航栏 -->
    <header class="sticky top-0 z-10 shadow bg-base-100">
      <div class="px-4 sm:px-6 md:px-8 flex items-center justify-between h-16 mx-auto max-w-[1400px]">
        <div class="flex items-center">
          <a href="#" class="flex items-center">
            <img src="/favicon.svg" alt="Stable Diffusion 模型管理器" class="h-7">
          </a>
          <!-- 主菜单 -->
          <nav class="ml-6 hidden md:block">
            <ul class="flex items-center gap-1">
              <li>
                <router-link 
                  to="/models" 
                  class="btn btn-sm" 
                  :class="[
                    isModelPage ? 'btn-primary' : 'btn-ghost'
                  ]"
                >
                  <span class="icon-[tabler--database] inline-block me-1.5 size-5"></span>
                  模型管理
                </router-link>
              </li>
              <!-- 这里可以添加更多导航项 -->
            </ul>
          </nav>
        </div>
        
        <div class="flex items-center gap-2">
          <!-- 主题切换 -->
          <button 
            type="button"
            class="btn btn-icon btn-outline"
            title="切换主题"
            @click="toggleDarkMode"
          >
            <span class="icon-[tabler--sun] size-5" v-if="!darkMode"></span>
            <span class="icon-[tabler--moon] size-5" v-else></span>
          </button>
          
          <!-- 移动端菜单按钮 -->
          <button 
            type="button"
            class="btn btn-icon btn-outline md:hidden"
            title="菜单"
            @click="toggleMobileMenu"
          >
            <span class="icon-[tabler--menu] size-5"></span>
          </button>
        </div>
      </div>
    </header>
    
    <!-- 移动端导航抽屉 -->
    <div 
      class="drawer-side z-20 md:hidden" 
      :class="{ 'drawer-open': mobileMenuOpen }"
    >
      <label 
        class="drawer-overlay" 
        @click="mobileMenuOpen = false"
      ></label>
      <div class="p-4 w-60 min-h-full bg-base-200 text-base-content">
        <div class="flex flex-col gap-2">
          <router-link 
            to="/models" 
            class="btn" 
            :class="[
              isModelPage ? 'btn-primary' : 'btn-ghost'
            ]"
            @click="mobileMenuOpen = false"
          >
            <span class="icon-[tabler--database] inline-block me-1.5 size-5"></span>
            模型管理
          </router-link>
          <!-- 这里可以添加更多导航项 -->
        </div>
      </div>
    </div>
    
    <!-- 页面内容区 -->
    <main class="flex-1 overflow-hidden">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';

// 获取当前路由
const route = useRoute();

// 当前是否在模型管理页面
const isModelPage = computed(() => route.path.startsWith('/models'));

// 移动端菜单状态
const mobileMenuOpen = ref(false);
const darkMode = ref(false);

// 切换移动端菜单
function toggleMobileMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value;
}

// 切换暗色模式
function toggleDarkMode() {
  darkMode.value = !darkMode.value;
  const theme = darkMode.value ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
}

// 生命周期钩子
onMounted(() => {
  // 从 localStorage 加载主题设置
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    darkMode.value = savedTheme === 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
  } else {
    // 检查系统主题偏好
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    darkMode.value = prefersDark;
    document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
  }
});
</script>

<style>
.drawer-side {
  position: fixed;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  transition: left 0.3s ease;
}

.drawer-side.drawer-open {
  left: 0;
}

.drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: -1;
}
</style> 
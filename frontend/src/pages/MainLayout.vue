<template>
  <div class="min-h-screen h-screen flex flex-col">
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
                    isModelPage ? 'btn-primary' : 'btn-soft'
                  ]"
                >
                  <span class="icon-[tabler--database] inline-block me-1.5 size-5"></span>
                  模型管理
                </router-link>
              </li>
              <li>
                <router-link 
                  to="/prompts" 
                  class="btn btn-sm" 
                  :class="[
                    isPromptPage ? 'btn-primary' : 'btn-soft'
                  ]"
                >
                  <span class="icon-[tabler--square-letter-p] inline-block me-1.5 size-5"></span>
                  提示词管理
                </router-link>
              </li>
              <!-- 这里可以添加更多导航项 -->
            </ul>
          </nav>
        </div>
        
        <div class="flex items-center gap-2">
          <!-- 使用独立的ComfyUI状态指示器组件，开启自动检查功能 -->
          <ComfyUIStatus
            v-model:status="comfyUIStatus"
            v-model:message="comfyUIMessage"
            :auto-check="true"
            :check-interval="10000"
          />
          
          <!-- 网络状态指示器组件 -->
          <NetworkStatus
            :auto-check="true"
            v-model:status="networkStatus"
          />
          
          <!-- 设置按钮 -->
          <button 
            type="button"
            class="btn btn-icon btn-outline"
            title="设置"
            @click="goToSettings"
          >
            <span class="icon-[tabler--settings] size-5"></span>
          </button>
          
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
            aria-haspopup="dialog"
            aria-expanded="false"
            aria-controls="mobile-drawer"
            data-overlay="#mobile-drawer"
          >
            <span class="icon-[tabler--menu-2] size-5"></span>
          </button>
        </div>
      </div>
    </header>
    
    <!-- 移动端导航抽屉 (使用Flyonui的drawer组件) -->
    <div 
      id="mobile-drawer" 
      class="overlay overlay-open:translate-x-0 drawer drawer-start hidden md:hidden" 
      role="dialog" 
      tabindex="-1"
    >
      <div class="drawer-header">
        <h3 class="drawer-title">导航菜单</h3>
        <button 
          type="button" 
          class="btn btn-text btn-circle btn-sm absolute end-3 top-3" 
          aria-label="关闭" 
          data-overlay="#mobile-drawer"
        >
          <span class="icon-[tabler--x] size-5"></span>
        </button>
      </div>
      <div class="drawer-body">
        <div class="flex flex-col gap-2">
          <router-link 
            to="/models" 
            class="btn btn-xl justify-start w-full" 
            :class="{ 'btn-primary': isModelPage }"
            data-overlay="#mobile-drawer"
          >
            <div class="w-8 flex justify-center">
              <span class="icon-[tabler--database] size-6"></span>
            </div>
            <span>模型管理</span>
          </router-link>
          <router-link 
            to="/prompts" 
            class="btn btn-xl justify-start w-full" 
            :class="{ 'btn-primary': isPromptPage }"
            data-overlay="#mobile-drawer"
          >
            <div class="w-8 flex justify-center">
              <span class="icon-[tabler--square-letter-p] size-6"></span>
            </div>
            <span>提示词管理</span>
          </router-link>
          <!-- 这里可以添加更多导航项 -->
        </div>
      </div>
      <div class="drawer-footer">
        <button type="button" class="btn btn-soft btn-secondary" data-overlay="#mobile-drawer">关闭</button>
      </div>
    </div>
    
    <!-- 页面内容区 -->
    <main class="flex-1 overflow-auto">
      <router-view />
    </main>
    
    <!-- 设置模态窗组件 -->
    <SettingsModal
      ref="settingsModalRef"
      :app-version="appVersion"
      :model-path="modelPath"
      @update:model-path="modelPath = $event"
      @scan-models="scanModels"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import SettingsModal from '../components/SettingsModal.vue';
import ComfyUIStatus from '../components/ComfyUIStatus.vue';
import NetworkStatus from '../components/NetworkStatus.vue';
import { ModelsAPI } from '../api/models';

// 使用Vue Router的API获取当前路由信息
const router = useRouter();
const route = useRoute();

// 当前是否在对应页面
const isModelPage = computed(() => route.path.startsWith('/models'));
const isPromptPage = computed(() => route.path.startsWith('/prompts'));

// 主题状态
const darkMode = ref(false);

// 设置相关状态
const appVersion = ref('');
const modelPath = ref('');
const settingsModalRef = ref<InstanceType<typeof SettingsModal> | null>(null);

// ComfyUI状态 - 初始化为unknown，将由组件负责更新
const comfyUIStatus = ref<'running' | 'stopped' | 'unknown'>('unknown');
const comfyUIMessage = ref('正在检查ComfyUI状态...');

// 网络状态显示控制
const networkStatus = ref<'success' | 'error' | 'warning' | 'unknown'>('unknown');

// 切换暗色模式
function toggleDarkMode() {
  darkMode.value = !darkMode.value;
  const theme = darkMode.value ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
}

// 打开设置模态框
function goToSettings() {
  if (settingsModalRef.value) {
    settingsModalRef.value.open();
  }
}

// 扫描模型
async function scanModels() {
  // 如果不在模型页面，先导航到模型页面
  if (!isModelPage.value) {
    router.push({ path: '/models' });
    // 导航后等待组件挂载完成再触发扫描
    setTimeout(() => {
      window.dispatchEvent(new CustomEvent('scan-models'));
    }, 300);
  } else {
    // 如果已经在模型页面，直接发射扫描事件
    window.dispatchEvent(new CustomEvent('scan-models'));
  }
}

// 生命周期钩子
onMounted(async () => {
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
  
  // 获取应用版本
  try {
    const versionInfo = await ModelsAPI.getVersion();
    appVersion.value = versionInfo.version;
  } catch (e) {
    console.error('获取版本信息失败', e);
    appVersion.value = ''; // 不显示默认版本号
  }
  
  // 加载模型目录
  try {
    modelPath.value = await ModelsAPI.getModelPath();
  } catch (e) {
    console.error('获取模型目录失败', e);
  }
});
</script>

<!--用于测试颜色的页面
http://localhost:5173/colors
-->
<template>
  <button class="btn btn-soft">Default</button>
<button class="btn btn-soft btn-primary">Primary</button>
<button class="btn btn-soft btn-secondary">Secondary</button>
<button class="btn btn-soft btn-accent">Accent</button>
<button class="btn btn-soft btn-info">Info</button>
<button class="btn btn-soft btn-success">Success</button>
<button class="btn btn-soft btn-warning">Warning</button>
<button class="btn btn-soft btn-error">Error</button>
  <div class="container mx-auto p-4 pb-20">
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h1 class="text-3xl font-bold text-base-content mb-6">FlyonUI 颜色系统示例</h1>
        <p class="text-base-content mb-8">本页面展示了 FlyonUI 中所有可用的颜色选项及其用途。颜色会根据当前的主题（亮色/暗色）自动适应。</p>
        
        <!-- 主要颜色部分 -->
        <h2 class="text-2xl font-semibold text-base-content mb-4">主要颜色</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
          <!-- Primary 色 -->
          <div class="card bg-primary shadow-md">
            <div class="card-body">
              <h3 class="card-title text-primary-content">Primary</h3>
              <p class="text-primary-content opacity-80">用于表示品牌或核心操作的主要颜色</p>
              <div class="mt-4">
                <span class="badge bg-primary-content text-primary mr-2">Primary Content</span>
                <button class="btn btn-sm btn-primary-content text-primary">按钮</button>
              </div>
            </div>
          </div>
          
          <!-- Secondary 色 -->
          <div class="card bg-secondary shadow-md">
            <div class="card-body">
              <h3 class="card-title text-secondary-content">Secondary</h3>
              <p class="text-secondary-content opacity-80">补充主色的辅助颜色，用于支持主色</p>
              <div class="mt-4">
                <span class="badge bg-secondary-content text-secondary mr-2">Secondary Content</span>
                <button class="btn btn-sm btn-secondary-content text-secondary">按钮</button>
              </div>
            </div>
          </div>
          
          <!-- Accent 色 -->
          <div class="card bg-accent shadow-md">
            <div class="card-body">
              <h3 class="card-title text-accent-content">Accent</h3>
              <p class="text-accent-content opacity-80">用于强调和突出关键UI元素的颜色</p>
              <div class="mt-4">
                <span class="badge bg-accent-content text-accent mr-2">Accent Content</span>
                <button class="btn btn-sm btn-accent-content text-accent">按钮</button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 基础颜色部分 -->
        <h2 class="text-2xl font-semibold text-base-content mb-4">基础颜色</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <!-- Base 100 -->
          <div class="card bg-base-100 border border-base-300 shadow-sm">
            <div class="card-body">
              <h3 class="card-title text-base-content">Base 100</h3>
              <p class="text-base-content opacity-80">最浅的表面颜色，适用于一般背景和页面内容</p>
              <div class="w-full h-8 bg-base-content mt-4 rounded-md flex items-center justify-center">
                <span class="text-base-100">Base Content</span>
              </div>
            </div>
          </div>
          
          <!-- Base 200 -->
          <div class="card bg-base-200 shadow-sm">
            <div class="card-body">
              <h3 class="card-title text-base-content">Base 200</h3>
              <p class="text-base-content opacity-80">稍深的底色，用于区分不同区域和元素</p>
              <div class="mt-4">
                <span class="badge bg-base-content text-base-200">Base Content</span>
              </div>
            </div>
          </div>
          
          <!-- Base 300 -->
          <div class="card bg-base-300 shadow-sm">
            <div class="card-body">
              <h3 class="card-title text-base-content">Base 300</h3>
              <p class="text-base-content opacity-80">用于更深的元素或阴影效果，创造层次感</p>
              <div class="mt-4">
                <div class="w-full h-8 bg-base-content rounded-md flex items-center justify-center">
                  <span class="text-base-300">Base Content</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 中性颜色 -->
        <h2 class="text-2xl font-semibold text-base-content mb-4">中性颜色</h2>
        <div class="card bg-neutral shadow-md mb-10">
          <div class="card-body">
            <h3 class="card-title text-neutral-content">Neutral</h3>
            <p class="text-neutral-content opacity-80">中性背景色，用于不太突出的元素或表面</p>
            <div class="mt-4">
              <span class="badge bg-neutral-content text-neutral mr-2">Neutral Content</span>
              <button class="btn btn-sm btn-neutral-content text-neutral">按钮</button>
            </div>
          </div>
        </div>
        
        <!-- 状态颜色部分 -->
        <h2 class="text-2xl font-semibold text-base-content mb-4">状态颜色</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
          <!-- Info 色 -->
          <div class="card bg-info shadow-md">
            <div class="card-body">
              <h3 class="card-title text-info-content">Info</h3>
              <p class="text-info-content opacity-80">用于信息性消息或UI中的有用提示</p>
              <div class="alert bg-info text-info-content mt-4 flex items-center">
                <span class="icon-[tabler--info-circle] size-5"></span>
                <span>这是一条信息提示</span>
              </div>
              <div class="mt-2">
                <span class="badge bg-info-content text-info mr-2">Info Content</span>
              </div>
            </div>
          </div>
          
          <!-- Success 色 -->
          <div class="card bg-success shadow-md">
            <div class="card-body">
              <h3 class="card-title text-success-content">Success</h3>
              <p class="text-success-content opacity-80">表示成功或积极状态，常用于成功消息</p>
              <div class="alert bg-success text-success-content mt-4 flex items-center">
                <span class="icon-[tabler--circle-check] size-5"></span>
                <span>操作已成功完成</span>
              </div>
              <div class="mt-2">
                <span class="badge bg-success-content text-success mr-2">Success Content</span>
              </div>
            </div>
          </div>
          
          <!-- Warning 色 -->
          <div class="card bg-warning shadow-md">
            <div class="card-body">
              <h3 class="card-title text-warning-content">Warning</h3>
              <p class="text-warning-content opacity-80">用于提醒用户注意潜在问题或警告</p>
              <div class="alert bg-warning text-warning-content mt-4 flex items-center">
                <span class="icon-[tabler--alert-triangle] size-5"></span>
                <span>请注意此警告信息</span>
              </div>
              <div class="mt-2">
                <span class="badge bg-warning-content text-warning mr-2">Warning Content</span>
              </div>
            </div>
          </div>
          
          <!-- Error 色 -->
          <div class="card bg-error shadow-md">
            <div class="card-body">
              <h3 class="card-title text-error-content">Error</h3>
              <p class="text-error-content opacity-80">表示错误或危险消息，通常用于警报或破坏性操作</p>
              <div class="alert bg-error text-error-content mt-4 flex items-center">
                <span class="icon-[tabler--alert-circle] size-5"></span>
                <span>发生错误，请重试</span>
              </div>
              <div class="mt-2">
                <span class="badge bg-error-content text-error mr-2">Error Content</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 颜色应用示例 -->
        <h2 class="text-2xl font-semibold text-base-content mb-4">颜色应用示例</h2>
        <div class="card bg-base-100 border border-base-300 shadow-xl mb-10">
          <div class="card-body">
            <h3 class="card-title mb-4">表单元素</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="form-control">
                <label class="label">
                  <span class="label-text">输入框示例</span>
                </label>
                <input type="text" placeholder="Primary 输入框" class="input input-bordered input-primary" />
                <input type="text" placeholder="Secondary 输入框" class="input input-bordered input-secondary mt-2" />
                <input type="text" placeholder="Accent 输入框" class="input input-bordered input-accent mt-2" />
              </div>
              
              <div class="form-control">
                <label class="label">
                  <span class="label-text">复选框和单选框</span>
                </label>
                <div class="flex flex-wrap gap-4">
                  <label class="flex items-center gap-2">
                    <input type="checkbox" class="checkbox checkbox-primary" />
                    <span>Primary</span>
                  </label>
                  <label class="flex items-center gap-2">
                    <input type="checkbox" class="checkbox checkbox-secondary" />
                    <span>Secondary</span>
                  </label>
                  <label class="flex items-center gap-2">
                    <input type="checkbox" class="checkbox checkbox-accent" />
                    <span>Accent</span>
                  </label>
                </div>
                
                <div class="flex flex-wrap gap-4 mt-4">
                  <label class="flex items-center gap-2">
                    <input type="radio" name="color-radio" class="radio radio-primary" />
                    <span>Primary</span>
                  </label>
                  <label class="flex items-center gap-2">
                    <input type="radio" name="color-radio" class="radio radio-secondary" />
                    <span>Secondary</span>
                  </label>
                  <label class="flex items-center gap-2">
                    <input type="radio" name="color-radio" class="radio radio-accent" />
                    <span>Accent</span>
                  </label>
                </div>
              </div>
            </div>
            
            <div class="divider"></div>
            
            <h3 class="card-title mb-4">按钮示例</h3>
            <div class="flex flex-wrap gap-2">
              <button class="btn btn-primary">Primary</button>
              <button class="btn btn-secondary">Secondary</button>
              <button class="btn btn-accent">Accent</button>
              <button class="btn btn-info">Info</button>
              <button class="btn btn-success">Success</button>
              <button class="btn btn-warning">Warning</button>
              <button class="btn btn-error">Error</button>
              <button class="btn btn-neutral">Neutral</button>
            </div>
            
            <div class="mt-4 flex flex-wrap gap-2">
              <button class="btn btn-outline btn-primary">Primary</button>
              <button class="btn btn-outline btn-secondary">Secondary</button>
              <button class="btn btn-outline btn-accent">Accent</button>
              <button class="btn btn-outline btn-info">Info</button>
              <button class="btn btn-outline btn-success">Success</button>
              <button class="btn btn-outline btn-warning">Warning</button>
              <button class="btn btn-outline btn-error">Error</button>
            </div>
            
            <div class="divider"></div>
            
            <h3 class="card-title mb-4">徽章示例</h3>
            <div class="flex flex-wrap gap-2">
              <span class="badge badge-primary">Primary</span>
              <span class="badge badge-secondary">Secondary</span>
              <span class="badge badge-accent">Accent</span>
              <span class="badge badge-info">Info</span>
              <span class="badge badge-success">Success</span>
              <span class="badge badge-warning">Warning</span>
              <span class="badge badge-error">Error</span>
              <span class="badge badge-neutral">Neutral</span>
            </div>
            
            <div class="divider"></div>
            
            <h3 class="card-title mb-4">文本颜色示例</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p class="text-primary">这是 Primary 文本颜色</p>
                <p class="text-secondary">这是 Secondary 文本颜色</p>
                <p class="text-accent">这是 Accent 文本颜色</p>
                <p class="text-neutral">这是 Neutral 文本颜色</p>
              </div>
              <div>
                <p class="text-info">这是 Info 文本颜色</p>
                <p class="text-success">这是 Success 文本颜色</p>
                <p class="text-warning">这是 Warning 文本颜色</p>
                <p class="text-error">这是 Error 文本颜色</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 主题切换部分 -->
        <div class="card bg-base-200 shadow-md">
          <div class="card-body">
            <h3 class="card-title">主题切换</h3>
            <p class="mb-4">尝试切换主题，查看颜色如何自动适应</p>
            <div class="flex items-center gap-2">
              <button class="btn" data-theme="light" @click="setTheme('light')">Light Theme</button>
              <button class="btn" data-theme="dark" @click="setTheme('dark')">Dark Theme</button>
              <button class="btn" @click="setSystemTheme()">跟随系统</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';

// 设置主题
const setTheme = (theme) => {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
};

// 跟随系统主题
const setSystemTheme = () => {
  localStorage.removeItem('theme');
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
};

onMounted(() => {
  // 从 localStorage 加载主题设置
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
  }
});
</script> 
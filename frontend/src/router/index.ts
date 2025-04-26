import { createRouter, createWebHistory } from 'vue-router'
import ModelManager from '../pages/ModelManager.vue'
import PromptManager from '../pages/PromptManager.vue'
// @ts-ignore 由于只在开发环境使用，可以忽略类型检查
import ColorDemo from '../pages/ColorDemo.vue'

// 定义路由配置
const routes = [
  {
    path: '/',
    redirect: '/models'
  },
  {
    path: '/models',
    name: 'ModelManager',
    component: ModelManager,
    meta: {
      title: '模型管理'
    }
  },
  {
    path: '/prompts',
    name: 'PromptManager',
    component: PromptManager,
    meta: {
      title: '提示词管理'
    }
  }
]

// 在开发环境中添加ColorDemo路由
if (import.meta.env.DEV) {
  routes.push({
    path: '/colors',
    name: 'ColorDemo',
    component: ColorDemo,
    meta: {
      title: 'FlyonUI 颜色系统示例'
    }
  })
}

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫，设置页面标题
router.beforeEach((to, _from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || 'SD模型管理器'}`
  next()
})

// 路由切换后重新初始化FlyonUI组件
router.afterEach(async (_to, _from, failure) => {
  if (!failure) setTimeout(() => window.HSStaticMethods?.autoInit?.(), 100);
});

export default router 
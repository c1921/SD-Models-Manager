import { createRouter, createWebHistory } from 'vue-router'
import ModelManager from '../pages/ModelManager.vue'

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
  // 可以在这里添加新的路由
  // {
  //   path: '/generate',
  //   name: 'ImageGeneration',
  //   component: () => import('../pages/ImageGeneration.vue'),
  //   meta: {
  //     title: '图像生成'
  //   }
  // },
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫，设置页面标题
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || 'SD模型管理器'}`
  next()
})

// 路由切换后重新初始化FlyonUI组件
router.afterEach(async (to, from, failure) => {
  if (!failure) setTimeout(() => window.HSStaticMethods?.autoInit?.(), 100);
});

export default router 
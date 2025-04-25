# SD Models Manager - 前端项目

本目录包含 SD Models Manager 的前端项目代码。

## 目录结构

```1
frontend/
├── public/         # 静态资源文件
├── src/            # 源代码
│   ├── api/        # API 接口定义
│   ├── assets/     # 静态资源
│   ├── components/ # Vue 组件
│   ├── pages/      # 页面组件
│   ├── router/     # 路由配置
│   └── utils/      # 工具函数
├── tests/          # 单元测试
└── ...             # 配置文件
```

## 工具函数

### 防抖工具 (debounce)

位于 `src/utils/debounce.ts`，提供两种防抖实现：

#### 1. useDebounce - 组合式API风格的防抖函数

提供完整的状态和控制能力，适合需要监视防抖状态的场景。

```typescript
import { useDebounce } from '../utils/debounce';

// 在组件中使用
setup() {
  // 创建防抖函数，延迟800ms
  const translateDebounce = useDebounce(async () => {
    // 这里是需要延迟执行的代码
    await fetchTranslation(text);
  }, 800);
  
  // 触发防抖
  function handleInput() {
    translateDebounce.triggerDebounce();
  }
  
  // 监听防抖状态
  const isLoading = computed(() => {
    return translateDebounce.isActive.value || translateDebounce.isExecuting.value;
  });
  
  // 组件卸载时取消防抖
  onBeforeUnmount(() => {
    translateDebounce.cancel();
  });
  
  return {
    handleInput,
    isLoading,
    // 可以直接返回防抖状态
    isTranslating: translateDebounce.isActive
  };
}
```

#### 2. debounce - 简单函数式防抖

适合简单场景，无需监视状态。

```typescript
import { debounce } from '../utils/debounce';

// 创建防抖函数
const debouncedSearch = debounce((query) => {
  searchAPI(query);
}, 500);

// 调用防抖函数
function handleSearch(query) {
  debouncedSearch(query);
}
```

### 防抖状态说明

`useDebounce` 提供的状态：

- `isActive`: 防抖是否处于等待执行阶段（延迟时间内）
- `isExecuting`: 回调函数是否正在执行中（特别适用于异步函数）

这两个状态可用于UI展示，例如显示"准备中..."或"执行中..."的提示。

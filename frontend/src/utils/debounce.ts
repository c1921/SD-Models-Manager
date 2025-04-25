import { ref } from 'vue';
import type { Ref } from 'vue';

/**
 * 防抖状态接口
 */
export interface DebounceState {
  isActive: Ref<boolean>;  // 防抖是否激活（等待执行）
  isExecuting: Ref<boolean>;  // 回调函数是否正在执行
  triggerDebounce: (...args: any[]) => void;  // 触发防抖函数
  cancel: () => void;  // 取消防抖
}

/**
 * 创建防抖函数
 * @param callback 需要执行的回调函数
 * @param delay 延迟时间（毫秒）
 * @returns 防抖状态对象
 */
export function useDebounce<T extends (...args: any[]) => any>(
  callback: T,
  delay: number = 800
): DebounceState {
  let timer: number | null = null;
  const isActive = ref(false);
  const isExecuting = ref(false);

  /**
   * 触发防抖函数
   * @param args 传递给回调函数的参数
   */
  const triggerDebounce = (...args: Parameters<T>) => {
    // 清除之前的定时器
    if (timer !== null) {
      clearTimeout(timer);
    }
    
    // 设置防抖激活状态
    isActive.value = true;
    
    // 设置新的定时器
    timer = window.setTimeout(async () => {
      try {
        isExecuting.value = true;
        await callback(...args);
      } catch (error) {
        console.error('防抖函数执行出错:', error);
      } finally {
        timer = null;
        isActive.value = false;
        isExecuting.value = false;
      }
    }, delay);
  };
  
  /**
   * 取消防抖，清除定时器
   */
  const cancel = () => {
    if (timer !== null) {
      clearTimeout(timer);
      timer = null;
      isActive.value = false;
    }
  };
  
  return {
    isActive,
    isExecuting,
    triggerDebounce,
    cancel
  };
}

/**
 * 创建防抖函数（简化版，无状态跟踪）
 * @param func 需要执行的函数
 * @param wait 延迟时间（毫秒）
 * @returns 防抖包装后的函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number = 800
): (...args: Parameters<T>) => void {
  let timeout: number | null = null;
  
  return function(...args: Parameters<T>) {
    if (timeout !== null) {
      clearTimeout(timeout);
    }
    
    timeout = window.setTimeout(() => {
      func(...args);
      timeout = null;
    }, wait);
  };
} 
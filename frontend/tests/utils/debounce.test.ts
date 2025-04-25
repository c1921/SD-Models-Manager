/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { debounce, useDebounce } from '../../src/utils/debounce';
import { nextTick } from 'vue';

describe('debounce.ts', () => {
  beforeEach(() => {
    // 设置vi.useFakeTimers()来模拟setTimeout
    vi.useFakeTimers();
  });

  afterEach(() => {
    // 恢复真实的定时器
    vi.restoreAllMocks();
  });

  describe('debounce', () => {
    it('应该延迟执行函数', async () => {
      const callback = vi.fn();
      const debouncedFn = debounce(callback, 500);

      // 调用函数
      debouncedFn();
      
      // 验证回调没有立即执行
      expect(callback).not.toBeCalled();
      
      // 前进500ms
      vi.advanceTimersByTime(500);
      
      // 验证回调被调用了一次
      expect(callback).toBeCalledTimes(1);
    });

    it('应该在多次调用时只执行一次', async () => {
      const callback = vi.fn();
      const debouncedFn = debounce(callback, 500);

      // 多次调用
      debouncedFn();
      debouncedFn();
      debouncedFn();
      
      // 前进250ms (不足以触发执行)
      vi.advanceTimersByTime(250);
      expect(callback).not.toBeCalled();
      
      // 再次调用 (重置定时器)
      debouncedFn();
      
      // 前进250ms (总共500ms，但从最后一次调用算起)
      vi.advanceTimersByTime(250);
      expect(callback).not.toBeCalled();
      
      // 再前进250ms，达到从最后一次调用起的500ms
      vi.advanceTimersByTime(250);
      expect(callback).toBeCalledTimes(1);
    });
  });

  describe('useDebounce', () => {
    it('应该提供正确的状态和方法', async () => {
      const callback = vi.fn();
      const { isActive, isExecuting, triggerDebounce, cancel } = useDebounce(callback, 500);
      
      // 检查初始状态
      expect(isActive.value).toBe(false);
      expect(isExecuting.value).toBe(false);
      
      // 触发防抖
      triggerDebounce();
      
      // 检查激活状态
      expect(isActive.value).toBe(true);
      expect(isExecuting.value).toBe(false);
      
      // 前进500ms
      vi.advanceTimersByTime(500);
      await nextTick();
      
      // 检查执行后状态
      expect(isActive.value).toBe(false);
      expect(callback).toBeCalledTimes(1);
      
      // 测试取消功能
      triggerDebounce();
      expect(isActive.value).toBe(true);
      
      cancel();
      expect(isActive.value).toBe(false);
      
      // 前进500ms，确认回调没有被执行
      vi.advanceTimersByTime(500);
      expect(callback).toBeCalledTimes(1); // 仍然是1，没有增加
    });
    
    it('应该处理异步回调函数', async () => {
      const asyncCallback = vi.fn().mockImplementation(() => {
        return new Promise(resolve => {
          setTimeout(resolve, 100);
        });
      });
      
      const { isActive, isExecuting, triggerDebounce } = useDebounce(asyncCallback, 500);
      
      // 触发防抖
      triggerDebounce();
      
      // 检查激活状态
      expect(isActive.value).toBe(true);
      
      // 前进500ms，触发回调
      vi.advanceTimersByTime(500);
      await nextTick();
      
      // 异步函数已经开始执行
      expect(isExecuting.value).toBe(true);
      expect(asyncCallback).toBeCalledTimes(1);
      
      // 等待异步操作完成
      vi.advanceTimersByTime(100);
      await nextTick();
      
      // 检查执行后状态
      expect(isActive.value).toBe(false);
      expect(isExecuting.value).toBe(false);
    });
  });
}); 
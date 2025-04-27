import { useToast } from 'vue-toastification';

// 获取toast实例
const toast = useToast();

// 导出简单的toast接口
export default {
  /**
   * 显示成功消息
   * @param message 消息内容
   */
  success(message: string) {
    toast.success(message);
  },

  /**
   * 显示错误消息
   * @param message 消息内容
   */
  error(message: string) {
    toast.error(message);
  },

  /**
   * 显示信息消息
   * @param message 消息内容
   */
  info(message: string) {
    toast.info(message);
  },

  /**
   * 显示警告消息
   * @param message 消息内容
   */
  warning(message: string) {
    toast.warning(message);
  }
};
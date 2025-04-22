import { Notyf } from 'notyf';

// 创建Notyf实例
const notyf = new Notyf({
  duration: 20000,
  position: {
    x: 'right',
    y: 'top'
  }
});

// 导出简单的toast接口
export default {
  /**
   * 显示成功消息
   * @param message 消息内容
   */
  success(message: string) {
    notyf.success(message);
  },

  /**
   * 显示错误消息
   * @param message 消息内容
   */
  error(message: string) {
    notyf.error(message);
  },

  /**
   * 显示信息消息 (使用success实现)
   * @param message 消息内容
   */
  info(message: string) {
    notyf.success(message);
  },

  /**
   * 显示警告消息 (使用error实现)
   * @param message 消息内容
   */
  warning(message: string) {
    notyf.error(message);
  }
};
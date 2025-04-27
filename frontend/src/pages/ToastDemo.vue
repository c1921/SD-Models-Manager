<template>
  <div class="container mx-auto px-4 py-8">
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title text-2xl mb-6">通知测试页面</h2>
        
        <!-- 基本通知类型 -->
        <div class="card bg-base-200">
          <div class="card-body">
            <h3 class="card-title text-lg mb-4">通知类型</h3>
            
            <div class="grid grid-cols-2 gap-4">
              <button class="btn btn-success" @click="showSuccess">成功通知</button>
              <button class="btn btn-error" @click="showError">错误通知</button>
              <button class="btn btn-info" @click="showInfo">信息通知</button>
              <button class="btn btn-warning" @click="showWarning">警告通知</button>
            </div>
          </div>
        </div>
        
        <!-- 自定义消息 -->
        <div class="card bg-base-200 mt-6">
          <div class="card-body">
            <h3 class="card-title text-lg mb-4">自定义消息</h3>
            
            <div class="flex flex-col gap-3">
              <div class="form-control">
                <label class="label">
                  <span class="label-text">消息内容</span>
                </label>
                <input v-model="customMessage" type="text" placeholder="请输入消息内容" class="input input-bordered" />
              </div>
              
              <div class="form-control">
                <label class="label">
                  <span class="label-text">通知类型</span>
                </label>
                <select v-model="selectedType" class="select select-bordered w-full">
                  <option value="success">成功</option>
                  <option value="error">错误</option>
                  <option value="info">信息</option>
                  <option value="warning">警告</option>
                </select>
              </div>
              
              <button class="btn btn-primary mt-2" @click="showCustomMessage">显示自定义消息</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import toast from '../utils/toast';

// 自定义消息相关状态
const customMessage = ref('这是一条自定义消息');
const selectedType = ref('success');

// 基本通知类型
function showSuccess() {
  toast.success('操作成功！');
}

function showError() {
  toast.error('操作失败！请重试。');
}

function showInfo() {
  toast.info('这是一条信息通知。');
}

function showWarning() {
  toast.warning('请注意，这是一条警告消息。');
}

// 显示自定义消息
function showCustomMessage() {
  if (!customMessage.value.trim()) {
    return toast.error('请输入消息内容');
  }
  
  switch (selectedType.value) {
    case 'success':
      toast.success(customMessage.value);
      break;
    case 'error':
      toast.error(customMessage.value);
      break;
    case 'info':
      toast.info(customMessage.value);
      break;
    case 'warning':
      toast.warning(customMessage.value);
      break;
  }
}
</script> 
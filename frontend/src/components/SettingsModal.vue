<template>
  <!-- 设置模态窗 -->
  <button 
    ref="settingsModalTrigger" 
    type="button" 
    class="hidden" 
    aria-haspopup="dialog" 
    aria-expanded="false" 
    aria-controls="settings-modal" 
    data-overlay="#settings-modal"
  ></button>

  <div 
    id="settings-modal" 
    class="overlay modal overlay-open:opacity-100 hidden overlay-open:duration-300" 
    role="dialog" 
    tabindex="-1"
  >
    <div class="modal-dialog overlay-open:opacity-100 overlay-open:duration-300">
      <div class="modal-content bg-base-100">
        <div class="modal-header border-b border-base-200">
          <h3 class="modal-title text-base-content">设置</h3>
          <button 
            type="button" 
            class="btn btn-text btn-circle btn-sm absolute end-3 top-3 text-base-content/70 hover:text-base-content" 
            aria-label="关闭" 
            data-overlay="#settings-modal"
          >
            <span class="icon-[tabler--x] size-5"></span>
          </button>
        </div>
        <div class="modal-body">
          <nav class="tabs tabs-bordered overflow-x-auto" aria-label="设置标签" role="tablist" aria-orientation="horizontal">
            <button 
              type="button" 
              class="tab active-tab:tab-active active text-base-content/70 active:text-base-content" 
              id="path-tab-item" 
              data-tab="#path-tab-content" 
              aria-controls="path-tab-content" 
              role="tab" 
              aria-selected="true"
            >
              <span class="icon-[tabler--folder] size-5 shrink-0 me-2"></span>
              路径设置
            </button>
            <button 
              type="button" 
              class="tab active-tab:tab-active text-base-content/70 active:text-base-content" 
              id="backup-tab-item" 
              data-tab="#backup-tab-content" 
              aria-controls="backup-tab-content" 
              role="tab" 
              aria-selected="false"
            >
              <span class="icon-[tabler--cloud-upload] size-5 shrink-0 me-2"></span>
              备份设置
            </button>
            <button 
              type="button" 
              class="tab active-tab:tab-active text-base-content/70 active:text-base-content" 
              id="about-tab-item" 
              data-tab="#about-tab-content" 
              aria-controls="about-tab-content" 
              role="tab" 
              aria-selected="false"
            >
              <span class="icon-[tabler--info-circle] size-5 shrink-0 me-2"></span>
              关于
            </button>
          </nav>
          
          <div class="mt-4">
            <div id="path-tab-content" role="tabpanel" aria-labelledby="path-tab-item">
              <div class="mb-6">
                <label for="modelPath" class="label">
                  <span class="label-text font-medium text-base-content">模型目录</span>
                </label>
                <div class="join w-full">
                  <button 
                    type="button" 
                    class="btn btn-primary join-item"
                    @click="selectPath"
                  >
                    <span class="icon-[tabler--folder-open] me-1.5 size-5"></span>
                    浏览
                  </button>
                  <input 
                    id="modelPath"
                    type="text" 
                    class="input input-bordered join-item flex-1 bg-base-100 text-base-content" 
                    placeholder="请选择模型目录" 
                    readonly 
                    :value="modelPath"
                  >
                  <button 
                    type="button" 
                    class="btn btn-primary join-item"
                    @click="scanModels"
                    data-overlay="#settings-modal"
                  >
                    <span class="icon-[tabler--radar] me-1.5 size-5"></span>
                    扫描模型
                  </button>
                </div>
              </div>
            </div>
            
            <div id="backup-tab-content" class="hidden" role="tabpanel" aria-labelledby="backup-tab-item">
              <div class="mb-6">
                <div class="form-control mb-4">
                  <label class="label cursor-pointer justify-start gap-2">
                    <input type="checkbox" class="toggle toggle-primary" v-model="webdavSettings.enabled" />
                    <span class="label-text font-medium text-base-content">启用WebDAV备份</span>
                  </label>
                  <p class="text-sm text-base-content/70 mt-1 ml-12">
                    定期将数据备份到WebDAV服务器
                  </p>
                </div>
                
                <div class="space-y-4" v-if="webdavSettings.enabled">
                  <div class="form-control w-full">
                    <label class="label">
                      <span class="label-text font-medium text-base-content">WebDAV服务器地址</span>
                    </label>
                    <input 
                      type="text" 
                      class="input input-bordered w-full bg-base-100 text-base-content" 
                      placeholder="例如: https://dav.example.com/remote.php/dav/files/username/" 
                      v-model="webdavSettings.url"
                    />
                  </div>
                  
                  <div class="form-control w-full">
                    <label class="label">
                      <span class="label-text font-medium text-base-content">用户名</span>
                    </label>
                    <input 
                      type="text" 
                      class="input input-bordered w-full bg-base-100 text-base-content" 
                      placeholder="WebDAV用户名" 
                      v-model="webdavSettings.username"
                    />
                  </div>
                  
                  <div class="form-control w-full">
                    <label class="label">
                      <span class="label-text font-medium text-base-content">密码</span>
                    </label>
                    <input 
                      type="password" 
                      class="input input-bordered w-full bg-base-100 text-base-content" 
                      placeholder="WebDAV密码" 
                      v-model="webdavSettings.password"
                    />
                  </div>
                  
                  <div class="flex gap-3">
                    <button 
                      type="button" 
                      class="btn btn-primary"
                      @click="testConnection"
                      :disabled="loading"
                    >
                      <span class="icon-[tabler--test-pipe] me-1.5 size-5"></span>
                      测试连接
                    </button>
                    
                    <button 
                      type="button" 
                      class="btn btn-primary"
                      @click="saveWebDAVSettings"
                      :disabled="loading || !canSave"
                    >
                      <span class="icon-[tabler--device-floppy] me-1.5 size-5"></span>
                      保存设置
                    </button>
                    
                    <button 
                      type="button" 
                      class="btn btn-primary"
                      @click="backupNow"
                      :disabled="loading || !isConfigured"
                    >
                      <span class="icon-[tabler--cloud-upload] me-1.5 size-5"></span>
                      立即备份
                    </button>
                  </div>
                  
                  <div v-if="backupStatus.last_backup" class="mt-2 text-sm text-base-content/70">
                    上次备份时间: {{ backupStatus.last_backup }}
                  </div>
                  
                  <div v-if="statusMessage" class="alert mt-3" :class="statusSuccess ? 'alert-success' : 'alert-error'">
                    <span>{{ statusMessage }}</span>
                  </div>
                  
                  <!-- 备份历史记录 -->
                  <div v-if="isConfigured && backupList.length > 0" class="mt-4">
                    <div class="divider">备份历史</div>
                    
                    <div class="overflow-x-auto">
                      <table class="table table-zebra">
                        <thead>
                          <tr>
                            <th>备份时间</th>
                            <th>文件名</th>
                            <th>操作</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="backup in backupList" :key="backup.filename">
                            <td>{{ backup.time }}</td>
                            <td class="truncate max-w-[200px]">{{ backup.filename }}</td>
                            <td>
                              <div class="flex gap-2">
                                <button 
                                  class="btn btn-sm btn-primary"
                                  @click="restoreBackup(backup.filename)"
                                  :disabled="loading"
                                >
                                  <span class="icon-[tabler--cloud-download] size-4"></span>
                                  恢复
                                </button>
                                <button 
                                  class="btn btn-sm btn-error"
                                  @click="deleteBackup(backup.filename)"
                                  :disabled="loading"
                                >
                                  <span class="icon-[tabler--trash] size-4"></span>
                                  删除
                                </button>
                              </div>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div id="about-tab-content" class="hidden" role="tabpanel" aria-labelledby="about-tab-item">
              <div class="flex flex-col items-center py-4">
                <img src="/favicon.svg" alt="logo" class="h-16 mb-3">
                <h5 class="text-lg font-medium mb-2 text-base-content">SD Models Manager</h5>
                <p class="text-base-content/80 mb-3">版本 <span>{{ appVersion }}</span></p>
                <p class="mb-2">
                  <a href="https://github.com/c1921/SD-Models-Manager" target="_blank" class="text-primary hover:text-primary-focus flex items-center">
                    <span class="icon-[tabler--brand-github] inline-block me-1.5 size-5"></span>
                    GitHub
                  </a>
                </p>
                <p class="text-sm text-base-content/60">MIT 开源许可 - 版权所有 (c) 2025</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ModelsAPI } from '../api/models';

// 属性和事件定义
defineProps<{
  appVersion: string;
  modelPath: string;
}>();

const emit = defineEmits<{
  'update:model-path': [path: string];
  'scan-models': [];
}>();

// WebDAV 相关状态
const webdavSettings = ref({
  enabled: false,
  url: '',
  username: '',
  password: ''
});

const backupStatus = ref({
  enabled: false,
  last_backup: null as string | null,
  url: '',
  username: ''
});

const backupList = ref<Array<{filename: string, time: string, timestamp: number}>>([]);
const loading = ref(false);
const statusMessage = ref('');
const statusSuccess = ref(false);

// 计算属性
const canSave = computed(() => {
  if (!webdavSettings.value.enabled) return true;
  return !!(webdavSettings.value.url && webdavSettings.value.username && webdavSettings.value.password);
});

const isConfigured = computed(() => {
  return backupStatus.value.enabled;
});

// 方法
async function selectPath() {
  try {
    const path = await ModelsAPI.selectModelPath();
    emit('update:model-path', path);
  } catch (e) {
    console.error('选择模型目录失败', e);
  }
}

function scanModels() {
  emit('scan-models');
}

async function loadWebDAVStatus() {
  try {
    loading.value = true;
    const response = await fetch('/api/webdav/status');
    const data = await response.json();
    
    backupStatus.value = data;
    webdavSettings.value.enabled = data.enabled;
    webdavSettings.value.url = data.url;
    webdavSettings.value.username = data.username;
    // 不再从后端加载密码，使用前端保存的密码
    // 如果密码为空并且已经启用了WebDAV，则提示用户可能需要重新输入密码
    if (!webdavSettings.value.password && data.enabled) {
      webdavSettings.value.password = localStorage.getItem('webdav_password') || '';
    }
    
    // 如果WebDAV已配置，加载备份列表
    if (data.enabled) {
      await loadBackupList();
    }
  } catch (e) {
    console.error('加载WebDAV状态失败', e);
  } finally {
    loading.value = false;
  }
}

async function loadBackupList() {
  try {
    const response = await fetch('/api/webdav/list');
    if (!response.ok) {
      console.error('获取备份列表失败', response.status);
      return;
    }
    
    const data = await response.json();
    console.log('获取到备份列表数据', data);
    
    if (Array.isArray(data)) {
      backupList.value = data;
      console.log(`当前显示 ${backupList.value.length} 个备份`);
    } else {
      console.error('备份列表数据格式不正确', data);
      backupList.value = [];
    }
  } catch (e) {
    console.error('加载备份列表失败', e);
    backupList.value = [];
  }
}

async function testConnection() {
  if (!canSave.value) {
    statusMessage.value = '请先填写完整的WebDAV配置';
    statusSuccess.value = false;
    return;
  }
  
  try {
    loading.value = true;
    const response = await fetch('/api/webdav/test', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: webdavSettings.value.url,
        username: webdavSettings.value.username,
        password: webdavSettings.value.password
      })
    });
    
    const result = await response.json();
    statusMessage.value = result.message;
    statusSuccess.value = result.success;
  } catch (e) {
    statusMessage.value = '连接测试失败';
    statusSuccess.value = false;
    console.error('测试WebDAV连接失败', e);
  } finally {
    loading.value = false;
  }
}

async function saveWebDAVSettings() {
  try {
    loading.value = true;
    
    // 在本地保存密码
    if (webdavSettings.value.password) {
      localStorage.setItem('webdav_password', webdavSettings.value.password);
    }
    
    const response = await fetch('/api/webdav/setup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: webdavSettings.value.url,
        username: webdavSettings.value.username,
        password: webdavSettings.value.password
      })
    });
    
    const result = await response.json();
    statusMessage.value = result.message;
    statusSuccess.value = result.success;
    
    if (result.success) {
      await loadWebDAVStatus();
    }
  } catch (e) {
    statusMessage.value = '保存设置失败';
    statusSuccess.value = false;
    console.error('保存WebDAV设置失败', e);
  } finally {
    loading.value = false;
  }
}

async function backupNow() {
  try {
    loading.value = true;
    statusMessage.value = '正在备份...';
    
    const response = await fetch('/api/webdav/backup', {
      method: 'POST'
    });
    
    const result = await response.json();
    statusMessage.value = result.message;
    statusSuccess.value = result.success;
    
    if (result.success) {
      await loadWebDAVStatus();
      // 等待一秒，确保服务器有时间处理新创建的备份文件
      setTimeout(async () => {
        await loadBackupList();
      }, 1000);
    }
  } catch (e) {
    statusMessage.value = '备份失败';
    statusSuccess.value = false;
    console.error('备份失败', e);
  } finally {
    loading.value = false;
  }
}

async function restoreBackup(filename: string) {
  if (!confirm(`确定要恢复备份 "${filename}"？这将覆盖当前数据。`)) {
    return;
  }
  
  try {
    loading.value = true;
    statusMessage.value = '正在恢复备份...';
    
    const response = await fetch('/api/webdav/restore', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        filename
      })
    });
    
    const result = await response.json();
    statusMessage.value = result.message;
    statusSuccess.value = result.success;
  } catch (e) {
    statusMessage.value = '恢复备份失败';
    statusSuccess.value = false;
    console.error('恢复备份失败', e);
  } finally {
    loading.value = false;
  }
}

async function deleteBackup(filename: string) {
  if (!confirm(`确定要删除备份 "${filename}"？此操作不可撤销。`)) {
    return;
  }
  
  try {
    loading.value = true;
    
    const response = await fetch(`/api/webdav/delete?filename=${encodeURIComponent(filename)}`, {
      method: 'DELETE'
    });
    
    const result = await response.json();
    statusMessage.value = result.message;
    statusSuccess.value = result.success;
    
    if (result.success) {
      await loadBackupList();
    }
  } catch (e) {
    statusMessage.value = '删除备份失败';
    statusSuccess.value = false;
    console.error('删除备份失败', e);
  } finally {
    loading.value = false;
  }
}

// 生命周期钩子
onMounted(() => {
  loadWebDAVStatus();
});

// 触发器引用
const settingsModalTrigger = ref<HTMLButtonElement | null>(null);

// 对外暴露的方法
function open() {
  if (settingsModalTrigger.value) {
    settingsModalTrigger.value.click();
  }
}

defineExpose({
  open
});
</script> 
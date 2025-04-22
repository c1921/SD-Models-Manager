# SD Models Manager

一个用于管理 Stable Diffusion 模型的工具，支持自动获取模型信息、预览图和筛选功能。

## 功能特点

- 🔍 自动扫描并识别模型文件
- 🖼️ 从 Civitai 获取模型信息和预览图
- 🏷️ 支持按类型和基础模型筛选
- 🌓 深色/浅色主题切换
- 👀 NSFW 内容过滤
- 📋 便捷的文件名复制功能
- 🔄 实时扫描进度显示
- 📱 响应式界面设计

## 使用方法

1. 下载并运行最新版本
2. 点击设置按钮，选择模型目录
3. 点击"扫描模型"开始扫描
4. 使用筛选器和搜索功能查找模型

## 支持的模型目录结构

在设置中选择 models 文件夹。

```text
models/
├── checkpoints/ # Stable Diffusion 模型
└── loras/ # LoRA 模型
```

## 下载

从 [Releases](https://github.com/c1921/SD-Models-Manager/releases/latest) 页面下载最新版本。

## 开发

### 环境要求

- Python 3.13+
- Node.js 20+
- npm 10+

### 快速启动（推荐）

使用开发辅助脚本同时启动前端和后端：

```bash
python run.py
```

这将自动：

- 启动后端API服务
- 启动前端Vite开发服务器
- 打开浏览器访问前端页面

可用选项：

- `--port <端口号>` - 指定后端API端口
- `--no-browser` - 不自动打开浏览器

```bash
# 示例：指定端口并不自动打开浏览器
python run.py --port 8000 --no-browser
```

### 分别启动（手动模式）

#### 后端开发

1. 安装Python依赖

   ```bash
   pip install -r requirements.txt
   ```

2. 运行开发服务器

   ```bash
   python main.py --dev
   ```

#### 前端开发

1. 进入前端目录

   ```bash
   cd frontend
   ```

2. 安装依赖

   ```bash
   npm install
   ```

3. 启动开发服务器

   ```bash
   npm run dev
   ```

前端开发服务器默认运行在 <http://localhost:5173>

### 构建应用

一键构建整个应用（包含前端和后端）：

```bash
python build.py
```

构建结果将在 `dist` 目录下生成。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

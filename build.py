import PyInstaller.__main__
import os
import shutil

# 确保 static 和 templates 目录存在
os.makedirs('static/images', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# 定义打包参数
PyInstaller.__main__.run([
    'model_manager.py',
    '--name=SD_Models_Manager',
    '--onefile',
    '--hidden-import=uvicorn.logging',
    '--hidden-import=uvicorn.lifespan.on',
    '--hidden-import=uvicorn.lifespan',
    '--add-data=templates;templates',
    '--add-data=static;static',
])

# 复制必要的目录到 dist 目录
if os.path.exists('dist/static'):
    shutil.rmtree('dist/static')
shutil.copytree('static', 'dist/static')

if os.path.exists('dist/templates'):
    shutil.rmtree('dist/templates')
shutil.copytree('templates', 'dist/templates') 
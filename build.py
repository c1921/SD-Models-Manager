import PyInstaller.__main__
import os
import shutil
import sys
from string import Template
from version import *

# 设置默认编码为 UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def clean_dist():
    """清理之前的构建文件"""
    output_name = f"SD_Prompt_Manager_v{VERSION_STR}"
    
    try:
        for item in ['dist', 'build']:
            if os.path.exists(item):
                shutil.rmtree(item)
                print(f"已删除 {item} 目录")
                
        for item in ['version_info.txt', 'runtime_hook.py', f'{output_name}.spec']:
            if os.path.exists(item):
                os.remove(item)
                print(f"已删除 {item} 文件")
                
    except Exception as e:
        print(f"清理文件时出错: {e}", file=sys.stderr)
        print("请手动关闭应用后重试", file=sys.stderr)
        exit(1)

def generate_version_info():
    """生成版本信息文件"""
    print(f"当前版本号: {VERSION_STR}")
    
    try:
        # 显式指定 UTF-8 编码
        with open('version_info.template', 'r', encoding='utf-8') as f:
            template = Template(f.read())
        
        version_tuple = VERSION + (0,)
        variables = {
            'VERSION_TUPLE': str(version_tuple),
            'VERSION_STR': VERSION_STR,
            'APP_NAME': APP_NAME,
            'COMPANY': COMPANY,
            'DESCRIPTION': DESCRIPTION,
            'COPYRIGHT': COPYRIGHT
        }
        
        # 显式指定 UTF-8 编码
        with open('version_info.txt', 'w', encoding='utf-8', errors='ignore') as f:
            f.write(template.substitute(variables))
            
    except Exception as e:
        print(f"生成版本信息时出错: {str(e)}", file=sys.stderr)
        raise

def prepare_directories():
    """准备必要的目录"""
    try:
        os.makedirs('static', exist_ok=True)
        os.makedirs('templates', exist_ok=True)
        print("目录准备完成")
    except Exception as e:
        print(f"创建目录时出错: {e}", file=sys.stderr)
        raise

def build_executable():
    """构建可执行文件"""
    output_name = f"SD_Prompt_Manager_v{VERSION_STR}"
    
    try:
        # 设置环境变量以确保正确的编码
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        PyInstaller.__main__.run([
            'model_manager.py',
            f'--name={output_name}',
            '--onefile',
            '--hidden-import=uvicorn.logging',
            '--hidden-import=uvicorn.lifespan.on',
            '--hidden-import=uvicorn.lifespan',
            '--add-data=templates;templates',
            '--add-data=static/favicon.svg;static',
        ])
        
        # 复制必要的文件到 dist 目录
        if os.path.exists('dist/static'):
            shutil.rmtree('dist/static')
        os.makedirs('dist/static')
        shutil.copy2('static/favicon.svg', 'dist/static/favicon.svg')

        if os.path.exists('dist/templates'):
            shutil.rmtree('dist/templates')
        shutil.copytree('templates', 'dist/templates')
        
        print(f"构建完成: dist/{output_name}.exe")
        
    except Exception as e:
        print(f"构建过程出错: {e}", file=sys.stderr)
        raise

def main():
    """主函数"""
    try:
        print("开始构建流程...")
        clean_dist()
        generate_version_info()
        prepare_directories()
        build_executable()
        print("构建流程完成!")
        
    except Exception as e:
        print(f"构建过程失败: {e}", file=sys.stderr)
        exit(1)

if __name__ == '__main__':
    main() 
import PyInstaller.__main__
import os
import shutil
import sys
import subprocess
from string import Template
from src.version.version import *
from pathlib import Path

# 设置默认编码为 UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def clean_dist():
    """清理之前的构建文件"""
    output_name = f"SD_Models_Manager_v{VERSION_STR}"
    
    try:
        # 清理构建目录
        for item in ['dist', 'build']:
            if os.path.exists(item):
                shutil.rmtree(item)
                print(f"已删除 {item} 目录")
                
        # 清理构建生成的文件
        for item in [
            'version_info.txt',
            'runtime_hook.py',
            f'{output_name}.spec',
            'SD_Models_Manager_v*.spec',  # 使用通配符匹配所有版本的 spec 文件
            '__pycache__',
            '**/__pycache__',
            '.pytest_cache',
            '.coverage'
        ]:
            # 使用 glob 处理通配符
            import glob
            for file in glob.glob(item, recursive=True):
                if os.path.isdir(file):
                    shutil.rmtree(file)
                else:
                    os.remove(file)
                print(f"已删除 {file}")
                
    except Exception as e:
        print(f"清理文件时出错: {e}", file=sys.stderr)
        print("请手动关闭应用后重试", file=sys.stderr)
        exit(1)

def generate_version_info():
    """生成版本信息文件"""
    print(f"当前版本号: {VERSION_STR}")
    
    try:
        # 显式指定 UTF-8 编码
        with open('src/version/version_info.template', 'r', encoding='utf-8') as f:
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

def build_frontend():
    """构建前端代码"""
    print("开始构建前端...")
    
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("错误: 未找到frontend目录", file=sys.stderr)
        return False
    
    # 设置环境变量为生产模式
    env = os.environ.copy()
    env["NODE_ENV"] = "production"
    
    # 进入前端目录安装依赖
    print("安装前端依赖...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    try:
        subprocess.run([npm_cmd, "install"], cwd=str(frontend_path), check=True)
    except subprocess.CalledProcessError as e:
        print(f"安装前端依赖失败: {e}", file=sys.stderr)
        return False
    
    # 构建前端
    print("执行构建...")
    try:
        subprocess.run([npm_cmd, "run", "build"], cwd=str(frontend_path), check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"构建前端失败: {e}", file=sys.stderr)
        return False
    
    # 检查构建输出目录是否存在
    frontend_dist = frontend_path / "dist"
    if not frontend_dist.exists():
        print("错误: 前端构建后的dist目录不存在", file=sys.stderr)
        return False
    
    # 为后端复制构建结果
    dist_path = Path("dist")
    dist_path.mkdir(exist_ok=True)
    frontend_public_path = dist_path / "frontend"
    
    # 删除旧的前端构建
    if frontend_public_path.exists():
        shutil.rmtree(frontend_public_path)
    
    # 复制新的前端构建
    shutil.copytree(frontend_dist, frontend_public_path)
    print(f"前端构建完成，输出位置: {frontend_public_path}")
    
    # 确保favicon.svg存在于构建目录中
    favicon_src = frontend_path / "public" / "favicon.svg"
    if favicon_src.exists():
        shutil.copy2(favicon_src, frontend_public_path / "favicon.svg")
        print("已复制favicon.svg到构建目录")
    else:
        # 尝试从static目录复制
        static_favicon = Path("static") / "favicon.svg"
        if static_favicon.exists():
            shutil.copy2(static_favicon, frontend_public_path / "favicon.svg")
            print("已从static目录复制favicon.svg到构建目录")
        else:
            print("警告: 未找到favicon.svg文件")
    
    return True

def prepare_directories():
    """准备必要的目录"""
    try:
        os.makedirs('static', exist_ok=True)
        os.makedirs('static/images', exist_ok=True)
        os.makedirs('dist', exist_ok=True)
        print("目录准备完成")
    except Exception as e:
        print(f"创建目录时出错: {e}", file=sys.stderr)
        raise

def build_executable():
    """构建可执行文件"""
    output_name = f"SD_Models_Manager_v{VERSION_STR}"
    
    try:
        # 设置环境变量以确保正确的编码
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # 构建前端
        if not build_frontend():
            print("警告: 前端构建失败，将只包含API部分")
        
        # 构建参数
        pyinstaller_args = [
            'main.py',
            f'--name={output_name}',
            '--onefile',
            '--hidden-import=uvicorn.logging',
            '--hidden-import=uvicorn.lifespan.on',
            '--hidden-import=uvicorn.lifespan',
            '--hidden-import=src.core.model_manager',
            '--hidden-import=src.api.model_api',
            '--hidden-import=src.utils.file_utils',
            '--hidden-import=src.utils.hash_utils'
        ]
        
        # 添加静态文件
        if os.path.exists('static'):
            pyinstaller_args.append('--add-data=static;static')
        
        # 添加前端构建
        if os.path.exists('dist/frontend'):
            pyinstaller_args.append('--add-data=dist/frontend;frontend')
        
        # 执行PyInstaller打包
        PyInstaller.__main__.run(pyinstaller_args)
        
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
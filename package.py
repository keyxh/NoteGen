#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用打包脚本
"""

import os
import sys
import shutil
import subprocess
import platform

def create_package():
    """创建应用包"""
    print("开始打包应用...")
    
    # 检查平台
    system = platform.system()
    
    # 创建打包目录
    package_dir = "code_dist"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # 复制必要文件
    print("复制应用文件...")
    shutil.copytree("backend", os.path.join(package_dir, "backend"))
    shutil.copytree("static", os.path.join(package_dir, "static"))
    shutil.copytree("templates", os.path.join(package_dir, "templates"))
    shutil.copy("main.py", os.path.join(package_dir, "main.py"))
    shutil.copy("requirements.txt", os.path.join(package_dir, "requirements.txt"))
    
    # 创建数据目录
    os.makedirs(os.path.join(package_dir, "data"), exist_ok=True)
    
    # 创建启动脚本
    if system == "Windows":
        # Windows启动脚本
        with open(os.path.join(package_dir, "start.bat"), "w") as f:
            f.write("@echo off\n")
            f.write("echo 正在启动Markdown编辑器...\n")
            f.write("python main.py\n")
            f.write("pause\n")
        
        # 创建安装脚本
        with open(os.path.join(package_dir, "install.bat"), "w") as f:
            f.write("@echo off\n")
            f.write("echo 正在安装依赖...\n")
            f.write("pip install -r requirements.txt\n")
            f.write("echo 安装完成！\n")
            f.write("pause\n")
            
    else:
        # Linux/Mac启动脚本
        with open(os.path.join(package_dir, "start.sh"), "w") as f:
            f.write("#!/bin/bash\n")
            f.write("echo 正在启动Markdown编辑器...\n")
            f.write("python3 main.py\n")
            
        # 设置执行权限
        os.chmod(os.path.join(package_dir, "start.sh"), 0o755)
        
        # 创建安装脚本
        with open(os.path.join(package_dir, "install.sh"), "w") as f:
            f.write("#!/bin/bash\n")
            f.write("echo 正在安装依赖...\n")
            f.write("pip3 install -r requirements.txt\n")
            f.write("echo 安装完成！\n")
            
        # 设置执行权限
        os.chmod(os.path.join(package_dir, "install.sh"), 0o755)
    
    # 创建README文件
    with open(os.path.join(package_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write("# Markdown编辑器\n\n")
        f.write("一个功能丰富的Markdown编辑器，支持AI助手和历史记录。\n\n")
        f.write("## 安装说明\n\n")
        
        if system == "Windows":
            f.write("1. 双击运行 `install.bat` 安装依赖\n")
            f.write("2. 双击运行 `start.bat` 启动应用\n")
        else:
            f.write("1. 运行 `chmod +x install.sh` 设置安装脚本权限\n")
            f.write("2. 运行 `./install.sh` 安装依赖\n")
            f.write("3. 运行 `./start.sh` 启动应用\n")
            
        f.write("\n## 功能特点\n\n")
        f.write("- 实时Markdown预览\n")
        f.write("- 文档历史记录\n")
        f.write("- AI助手集成\n")
        f.write("- 本地数据存储\n")
        f.write("- 响应式界面\n")
    
    print(f"打包完成！输出目录: {os.path.abspath(package_dir)}")
    
    # 询问是否创建压缩包
    if system == "Windows":
        try:
            import zipfile
            
            zip_name = "md_editor.zip"
            print(f"正在创建压缩包: {zip_name}")
            
            with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(package_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(package_dir))
                        zipf.write(file_path, arcname)
            
            print(f"压缩包创建完成: {os.path.abspath(zip_name)}")
            
            # 打开包含压缩包的文件夹
            try:
                os.startfile(os.path.dirname(os.path.abspath(zip_name)))
                print(f"已打开文件夹: {os.path.dirname(os.path.abspath(zip_name))}")
            except Exception as e:
                print(f"无法打开文件夹: {e}")
        except ImportError:
            print("无法创建压缩包，缺少zipfile模块")
    else:
        try:
            print("正在创建压缩包: md_editor.tar.gz")
            subprocess.run(["tar", "-czf", "md_editor.tar.gz", "-C", os.path.dirname(package_dir), os.path.basename(package_dir)], check=True)
            print(f"压缩包创建完成: {os.path.abspath('md_editor.tar.gz')}")
            
            # 打开包含压缩包的文件夹
            try:
                subprocess.run(["xdg-open", os.path.dirname(os.path.abspath('md_editor.tar.gz'))], check=True)
                print(f"已打开文件夹: {os.path.dirname(os.path.abspath('md_editor.tar.gz'))}")
            except Exception as e:
                print(f"无法打开文件夹: {e}")
        except subprocess.CalledProcessError:
            print("无法创建压缩包")
    
    print("\n打包流程完成！")
    
    # 打开打包文件夹
    try:
        if system == "Windows":
            os.startfile(os.path.abspath(package_dir))
            print(f"已打开打包文件夹: {os.path.abspath(package_dir)}")
        elif system == "Darwin":  # macOS
            subprocess.run(["open", os.path.abspath(package_dir)], check=True)
            print(f"已打开打包文件夹: {os.path.abspath(package_dir)}")
        else:  # Linux
            subprocess.run(["xdg-open", os.path.abspath(package_dir)], check=True)
            print(f"已打开打包文件夹: {os.path.abspath(package_dir)}")
    except Exception as e:
        print(f"无法打开文件夹: {e}")
        print(f"请手动打开: {os.path.abspath(package_dir)}")

if __name__ == "__main__":
    create_package()
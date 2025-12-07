#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown编辑器打包脚本
使用PyInstaller将应用打包为单个可执行文件
"""

import os
import sys
import subprocess
import shutil
import platform
import sqlite3
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        result = subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"PyInstaller已安装，版本: {result.stdout.strip()}")
            return True
    except Exception:
        pass
    
    print("PyInstaller未安装，正在安装...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller安装成功")
        return True
    except Exception as e:
        print(f"PyInstaller安装失败: {e}")
        return False

def clear_database_data(db_path):
    """清空指定路径数据库中的数据，但保留表结构"""
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # 清空每个表的数据
        for table in tables:
            table_name = table[0]
            if table_name != 'sqlite_sequence':  # 跳过系统表
                cursor.execute(f"DELETE FROM {table_name};")
                print(f"已清空表 {table_name} 的数据")
        
        # 重置自增ID
        cursor.execute("DELETE FROM sqlite_sequence;")
        
        # 提交更改
        conn.commit()
        conn.close()
        
        print("数据库数据清空完成")
        return True
    except Exception as e:
        print(f"清空数据库数据失败: {e}")
        return False

def copy_data_directory():
    """将data目录复制到dist文件夹"""
    source_dir = os.path.join(os.getcwd(), "data")
    target_dir = os.path.join(os.getcwd(), "dist", "data")
    
    if not os.path.exists(source_dir):
        print(f"源目录不存在: {source_dir}")
        return False
    
    try:
        # 如果目标目录已存在，先删除
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        
        # 复制整个目录
        shutil.copytree(source_dir, target_dir)
        print(f"已将data目录复制到: {target_dir}")
        return True
    except Exception as e:
        print(f"复制data目录失败: {e}")
        return False

def copy_static_and_template_directories():
    """将static和templates目录复制到dist文件夹"""
    # 复制static目录
    source_static = os.path.join(os.getcwd(), "static")
    target_static = os.path.join(os.getcwd(), "dist", "static")
    
    if os.path.exists(source_static):
        try:
            if os.path.exists(target_static):
                shutil.rmtree(target_static)
            shutil.copytree(source_static, target_static)
            print(f"已将static目录复制到: {target_static}")
        except Exception as e:
            print(f"复制static目录失败: {e}")
    
    # 复制templates目录
    source_templates = os.path.join(os.getcwd(), "templates")
    target_templates = os.path.join(os.getcwd(), "dist", "templates")
    
    if os.path.exists(source_templates):
        try:
            if os.path.exists(target_templates):
                shutil.rmtree(target_templates)
            shutil.copytree(source_templates, target_templates)
            print(f"已将templates目录复制到: {target_templates}")
        except Exception as e:
            print(f"复制templates目录失败: {e}")
    
    return True

def build_executable():
    """使用PyInstaller构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 使用规范文件构建
    cmd = [sys.executable, "-m", "PyInstaller", "build_exe.spec", "--clean"]
    
    try:
        subprocess.check_call(cmd)
        print("可执行文件构建成功")
        
        # 复制data目录到dist文件夹
        if copy_data_directory():
            print("data目录复制成功")
        else:
            print("警告: data目录复制失败")
        
        # 复制static和templates目录到dist文件夹
        if copy_static_and_template_directories():
            print("static和templates目录复制成功")
        else:
            print("警告: static和templates目录复制失败")
        
        # 清空dist目录中数据库的数据
        dist_db_path = os.path.join(os.getcwd(), "dist", "data", "md_editor.db")
        if clear_database_data(dist_db_path):
            print("dist目录中数据库数据清空成功")
        else:
            print("警告: dist目录中数据库数据清空失败")
            
        return True
    except Exception as e:
        print(f"构建失败: {e}")
        return False

def open_output_folder():
    """打开输出文件夹"""
    output_dir = os.path.join(os.getcwd(), "dist")
    if os.path.exists(output_dir):
        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(output_dir)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", output_dir])
            else:  # Linux
                subprocess.run(["xdg-open", output_dir])
            print(f"已打开输出文件夹: {output_dir}")
        except Exception as e:
            print(f"无法打开输出文件夹: {e}")
    else:
        print(f"输出文件夹不存在: {output_dir}")

def main():
    """主函数"""
    print("Markdown编辑器打包工具")
    print("=" * 50)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        print("无法继续，请手动安装PyInstaller")
        return
    
    # 构建可执行文件
    if build_executable():
        print("\n打包完成！")
        print("可执行文件位于 dist/MarkdownEditor.exe")
        open_output_folder()
    else:
        print("\n打包失败，请检查错误信息")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置
"""

import os
import logging
import sys

# 配置日志
logger = logging.getLogger('app.config')

def resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和打包后的环境"""
    try:
        # PyInstaller创建的临时文件夹路径
        base_path = sys._MEIPASS
    except AttributeError:
        # 正常的开发环境
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)

def get_executable_dir():
    """获取可执行文件所在目录"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        # 使用sys._MEIPASS获取PyInstaller创建的临时文件夹
        # 但我们需要的是可执行文件所在的目录，而不是临时文件夹
        return os.path.dirname(sys.executable)
    else:
        # 如果是开发环境
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    """应用配置类"""
    
    # 获取可执行文件所在目录
    EXECUTABLE_DIR = get_executable_dir()
    
    # 数据库配置
    DATABASE_PATH = os.path.join(EXECUTABLE_DIR, 'data', 'md_editor.db')
    
    # OpenAI API默认配置
    OPENAI_CONFIG = {
        "api_key": "sk-P8Cm1QYbS0mRPDRl7yCUI0SXC12QQn12BWK0QSnnTo4SWwPc",
        "base_url": "https://api.hunyuan.cloud.tencent.com/v1",
        "model": "hunyuan-lite",
        "temperature": 0.7,
        "max_tokens": 2000,
        "timeout": 30
    }
    
    # 应用默认配置
    DEFAULT_APP_CONFIG = {
        "host": "127.0.0.1",
        "port": 5000,
        "debug": False,
        "auto_save": True,
        "auto_save_interval": 30,
        "theme": "light",
        "font_size": 14,
        "tab_size": 4,
        "word_wrap": True,
        "preview_theme": "github",
        "sync_scroll": True,
        "highlight_code": True
    }
    
    # 配置文件路径
    CONFIG_FILE = os.path.join(EXECUTABLE_DIR, 'data', 'config.json')
    APP_CONFIG_FILE = os.path.join(EXECUTABLE_DIR, 'data', 'app_config.json')
    
    # 静态文件目录
    STATIC_DIR = os.path.join(EXECUTABLE_DIR, 'static')
    
    # 模板目录
    TEMPLATE_DIR = os.path.join(EXECUTABLE_DIR, 'templates')
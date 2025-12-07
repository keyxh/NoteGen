#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown编辑器主入口
使用WebView显示前端界面
"""

import os
import sys
import threading
import webview
import logging
import signal
import requests
import time
import socket
from backend.app import create_app
from backend.config_manager import ConfigManager
from backend.log_manager import log_manager

# 配置日志
logger = logging.getLogger('app')

# 全局变量，用于跟踪后端进程和Flask应用
backend_app = None
backend_thread = None
shutdown_event = threading.Event()

def get_executable_dir():
    """获取可执行文件所在目录，兼容开发和打包环境"""
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    """获取资源的绝对路径，支持开发环境和打包后的环境"""
    # try:
    #     # PyInstaller创建的临时文件夹
    #     base_path = sys._MEIPASS
    # except Exception:
    #     # 正常的开发环境
    #     base_path = os.path.abspath(".")
    base_path = get_executable_dir()
    return os.path.join(base_path, relative_path)

def is_port_in_use(port, host='127.0.0.1'):
    """检查端口是否已被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True

def start_backend():
    """启动后端Flask服务"""
    global backend_app
    logger.debug("正在启动后端Flask服务...")
    backend_app = create_app()
    
    # 获取应用配置
    config_manager = ConfigManager()
    app_config = config_manager.get_app_config()
    
    host = app_config.get('host', '127.0.0.1')
    port = app_config.get('port', 5000)
    debug = app_config.get('debug', False)
    
    logger.debug(f"后端Flask服务启动成功，监听地址: http://{host}:{port}")
    
    # 使用shutdown_event来控制服务运行
    def run_server():
        backend_app.run(host=host, port=port, debug=debug, use_reloader=False, threaded=True)
    
    # 在单独的线程中运行服务器
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # 等待关闭事件
    shutdown_event.wait()
    
    # 尝试关闭服务器
    try:
        requests.post(f'http://{host}:{port}/shutdown', timeout=5)
    except:
        pass
    
    logger.debug("后端服务已关闭")

def main():
    """主函数"""
    global backend_thread
    logger.info("启动Markdown编辑器...")
    
    # 设置关闭信号处理
    def signal_handler(sig, frame):
        logger.debug("接收到关闭信号，正在关闭后端服务...")
        shutdown_event.set()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 确保数据库和配置目录存在
    data_dir = resource_path('data')
    os.makedirs(data_dir, exist_ok=True)
    logger.debug("数据目录已准备就绪")
    
    # 获取应用配置
    config_manager = ConfigManager()
    app_config = config_manager.get_app_config()
    
    host = app_config.get('host', '127.0.0.1')
    port = app_config.get('port', 5000)
    
    # 检查端口是否已被占用
    backend_already_running = is_port_in_use(port, host)
    
    if not backend_already_running:
        # 启动后端服务线程
        logger.debug("正在启动后端服务线程...")
        backend_thread = threading.Thread(target=start_backend, daemon=False)
        backend_thread.start()
        
        # 等待后端启动 - 减少等待时间
        time.sleep(1.0)
    else:
        logger.info(f"检测到后端服务已在 http://{host}:{port} 运行，跳过启动")
    
    # 创建WebView窗口
    logger.debug("正在创建WebView窗口...")
    window = webview.create_window(
        'Markdown编辑器',
        f'http://{host}:{port}',
        width=1800,  # 增加宽度
        height=900,  # 增加高度
        resizable=True,
        # 添加关闭确认对话框
        confirm_close=True
    )
    
    # 启动WebView
    logger.debug("启动WebView...")
    webview.start()
    
    # 窗口关闭后执行清理
    on_window_closed(backend_already_running)
    
    # 只有在后端服务是由我们启动的情况下才关闭它
    if not backend_already_running:
        shutdown_event.set()
        if backend_thread and backend_thread.is_alive():
            backend_thread.join(timeout=5)
    
    # 应用退出时记录日志
    logger.debug("Markdown编辑器已退出")

def on_window_closed(backend_already_running=False):
    """窗口关闭时的回调函数"""
    global backend_thread, shutdown_event
    logger.debug("WebView窗口已关闭，正在关闭后端服务...")
    
    # 只有在后端服务是由我们启动的情况下才关闭它
    if not backend_already_running:
        shutdown_event.set()
        
        # 等待后端线程结束
        if backend_thread and backend_thread.is_alive():
            backend_thread.join(timeout=5)
            if backend_thread.is_alive():
                logger.warning("后端线程未能在5秒内正常关闭")
        
        logger.debug("后端服务已关闭")
    else:
        logger.debug("后端服务不是由本实例启动的，跳过关闭")

if __name__ == '__main__':
    main()
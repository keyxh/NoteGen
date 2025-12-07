#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理器
提供日志记录、查看和管理功能
"""

import os
import logging
import logging.handlers
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from backend.config import Config

class LogManager:
    """日志管理器类"""
    
    def __init__(self, log_dir=None):
        """初始化日志管理器
        
        Args:
            log_dir: 日志目录，如果为None则使用Config中的路径
        """
        # 使用Config中的路径，如果没有提供log_dir参数
        if log_dir is None:
            self.log_dir = os.path.join(Config.EXECUTABLE_DIR, 'data', 'logs')
        else:
            self.log_dir = log_dir
            
        self.ensure_log_dir()
        
        # 配置应用日志
        self.setup_app_logger()
        
        # 配置访问日志
        self.setup_access_logger()
        
        # 配置错误日志
        self.setup_error_logger()
    
    def ensure_log_dir(self):
        """确保日志目录存在"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def setup_app_logger(self):
        """设置应用日志记录器"""
        self.app_logger = logging.getLogger('app')
        self.app_logger.setLevel(logging.INFO)
        
        # 避免重复添加处理器
        if not self.app_logger.handlers:
            # 文件处理器，按大小轮转
            file_handler = logging.handlers.RotatingFileHandler(
                os.path.join(self.log_dir, 'app.log'),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO)
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 设置格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加处理器
            self.app_logger.addHandler(file_handler)
            self.app_logger.addHandler(console_handler)
    
    def setup_access_logger(self):
        """设置访问日志记录器"""
        self.access_logger = logging.getLogger('access')
        self.access_logger.setLevel(logging.INFO)
        
        # 避免重复添加处理器
        if not self.access_logger.handlers:
            # 文件处理器，按时间轮转
            file_handler = logging.handlers.TimedRotatingFileHandler(
                os.path.join(self.log_dir, 'access.log'),
                when='midnight',
                interval=1,
                backupCount=30,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO)
            
            # 设置格式
            formatter = logging.Formatter(
                '%(asctime)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            # 添加处理器
            self.access_logger.addHandler(file_handler)
    
    def setup_error_logger(self):
        """设置错误日志记录器"""
        self.error_logger = logging.getLogger('error')
        self.error_logger.setLevel(logging.ERROR)
        
        # 避免重复添加处理器
        if not self.error_logger.handlers:
            # 文件处理器，按大小轮转
            file_handler = logging.handlers.RotatingFileHandler(
                os.path.join(self.log_dir, 'error.log'),
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.ERROR)
            
            # 设置格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n'
                '文件: %(pathname)s, 行号: %(lineno)d, 函数: %(funcName)s\n'
            )
            file_handler.setFormatter(formatter)
            
            # 添加处理器
            self.error_logger.addHandler(file_handler)
    
    def get_log_files(self) -> List[Dict[str, str]]:
        """获取所有日志文件列表
        
        Returns:
            日志文件列表，每个元素包含文件名和路径
        """
        log_files = []
        
        for file_name in os.listdir(self.log_dir):
            if file_name.endswith('.log'):
                file_path = os.path.join(self.log_dir, file_name)
                stat = os.stat(file_path)
                
                log_files.append({
                    'name': file_name,
                    'path': file_path,
                    'size': self.format_file_size(stat.st_size),
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return sorted(log_files, key=lambda x: x['modified'], reverse=True)
    
    def get_log_content(self, file_name: str, lines: int = 100) -> Dict[str, any]:
        """获取日志文件内容
        
        Args:
            file_name: 日志文件名
            lines: 读取的行数
            
        Returns:
            包含日志内容和元数据的字典
        """
        file_path = os.path.join(self.log_dir, file_name)
        
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': f'日志文件 {file_name} 不存在'
            }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 读取最后N行
                all_lines = f.readlines()
                content_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
                return {
                    'success': True,
                    'content': ''.join(content_lines),
                    'total_lines': len(all_lines),
                    'showed_lines': len(content_lines),
                    'file_size': self.format_file_size(os.path.getsize(file_path))
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'读取日志文件失败: {str(e)}'
            }
    
    def search_logs(self, keyword: str, file_name: Optional[str] = None, max_results: int = 100) -> Dict[str, any]:
        """搜索日志内容
        
        Args:
            keyword: 搜索关键词
            file_name: 指定日志文件名，None表示搜索所有文件
            max_results: 最大结果数
            
        Returns:
            包含搜索结果的字典
        """
        results = []
        
        # 确定要搜索的文件
        if file_name:
            files_to_search = [file_name] if os.path.exists(os.path.join(self.log_dir, file_name)) else []
        else:
            files_to_search = [f for f in os.listdir(self.log_dir) if f.endswith('.log')]
        
        for file_name in files_to_search:
            file_path = os.path.join(self.log_dir, file_name)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if keyword.lower() in line.lower():
                            results.append({
                                'file': file_name,
                                'line_num': line_num,
                                'content': line.strip()
                            })
                            
                            if len(results) >= max_results:
                                break
            except Exception as e:
                pass
        
        return {
            'success': True,
            'results': results,
            'total': len(results)
        }
    
    def clear_logs(self, file_name: Optional[str] = None) -> Dict[str, any]:
        """清空日志文件
        
        Args:
            file_name: 指定日志文件名，None表示清空所有文件
            
        Returns:
            操作结果
        """
        try:
            if file_name:
                # 清空指定文件
                file_path = os.path.join(self.log_dir, file_name)
                if os.path.exists(file_path):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('')
                    return {
                        'success': True,
                        'message': f'日志文件 {file_name} 已清空'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'日志文件 {file_name} 不存在'
                    }
            else:
                # 清空所有日志文件
                for file_name in os.listdir(self.log_dir):
                    if file_name.endswith('.log'):
                        file_path = os.path.join(self.log_dir, file_name)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write('')
                
                return {
                    'success': True,
                    'message': '所有日志文件已清空'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'清空日志失败: {str(e)}'
            }
    
    def delete_logs(self, file_name: Optional[str] = None) -> Dict[str, any]:
        """删除日志文件
        
        Args:
            file_name: 指定日志文件名，None表示删除所有文件
            
        Returns:
            操作结果
        """
        try:
            if file_name:
                # 删除指定文件
                file_path = os.path.join(self.log_dir, file_name)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return {
                        'success': True,
                        'message': f'日志文件 {file_name} 已删除'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'日志文件 {file_name} 不存在'
                    }
            else:
                # 删除所有日志文件
                for file_name in os.listdir(self.log_dir):
                    if file_name.endswith('.log'):
                        file_path = os.path.join(self.log_dir, file_name)
                        os.remove(file_path)
                
                return {
                    'success': True,
                    'message': '所有日志文件已删除'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'删除日志失败: {str(e)}'
            }
    
    def pack_logs(self, output_dir: str = 'data') -> Dict[str, any]:
        """打包日志文件
        
        Args:
            output_dir: 输出目录
            
        Returns:
            操作结果
        """
        try:
            import zipfile
            import uuid
            import platform
            import subprocess
            
            # 创建压缩文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            zip_filename = f'logs_{timestamp}_{uuid.uuid4().hex[:8]}.zip'
            zip_path = os.path.join(output_dir, zip_filename)
            
            # 创建压缩文件
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_name in os.listdir(self.log_dir):
                    if file_name.endswith('.log'):
                        file_path = os.path.join(self.log_dir, file_name)
                        zipf.write(file_path, file_name)
            
            # 自动打开存放zip文件的文件夹
            try:
                if platform.system() == 'Windows':
                    os.startfile(os.path.dirname(os.path.abspath(zip_path)))
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(["open", os.path.dirname(os.path.abspath(zip_path))])
                else:  # Linux
                    subprocess.run(["xdg-open", os.path.dirname(os.path.abspath(zip_path))])
            except Exception as e:
                # 如果打开文件夹失败，不影响打包结果
                pass
            
            return {
                'success': True,
                'message': f'日志已打包到 {zip_filename}',
                'file_path': zip_path,
                'file_size': self.format_file_size(os.path.getsize(zip_path))
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'打包日志失败: {str(e)}'
            }
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """格式化文件大小
        
        Args:
            size_bytes: 字节数
            
        Returns:
            格式化后的文件大小字符串
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

# 创建全局日志管理器实例
log_manager = LogManager()
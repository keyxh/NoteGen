#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用主文件
"""

from flask import Flask, request, jsonify, send_from_directory, render_template, send_file
from flask_cors import CORS
import os
import sys
import logging
import json
from backend.database import DBManager
from backend.ai_service import AIService
from backend.config_manager import ConfigManager
from backend.log_manager import LogManager

# 配置日志
logger = logging.getLogger('app')

def resource_path(relative_path):
    """获取资源的绝对路径，支持开发环境和打包后的环境"""
    try:
        # PyInstaller创建的临时文件夹
        base_path = sys._MEIPASS
    except Exception:
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

def create_app():
    """创建Flask应用"""
    logger.info("正在创建Flask应用...")
    
    # 获取可执行文件所在目录
    executable_dir = get_executable_dir()
    
    # 获取模板和静态文件的路径
    template_folder = os.path.join(executable_dir, 'templates')
    static_folder = os.path.join(executable_dir, 'static')
    
    app = Flask(__name__, 
                template_folder=template_folder,
                static_folder=static_folder)
    
    # 启用CORS，明确允许所有HTTP方法
    CORS(app, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # 全局变量，用于存储管理器实例
    app.db_manager = None
    app.ai_service = None
    app.config_manager = None
    app.log_manager = None
    
    # 延迟初始化函数
    def get_db_manager():
        if app.db_manager is None:
            logger.info("正在初始化数据库管理器...")
            app.db_manager = DBManager()
        return app.db_manager
    
    def get_ai_service():
        if app.ai_service is None:
            logger.info("正在初始化AI服务...")
            app.ai_service = AIService()
        return app.ai_service
    
    def get_config_manager():
        if app.config_manager is None:
            logger.info("正在初始化配置管理器...")
            app.config_manager = ConfigManager()
        return app.config_manager
    
    def get_log_manager():
        if app.log_manager is None:
            logger.info("正在初始化日志管理器...")
            app.log_manager = LogManager()
        return app.log_manager
    
    logger.info("Flask应用创建完成")
    
    # 路由：主页
    @app.route('/')
    def index():
        logger.info("访问主页")
        return render_template('index.html')
    
    # 路由：获取所有文档
    @app.route('/api/documents', methods=['GET'])
    def get_documents():
        logger.info("获取所有文档列表")
        db_manager = get_db_manager()
        documents = db_manager.get_all_documents()
        logger.info(f"成功获取 {len(documents)} 个文档")
        return jsonify({'success': True, 'documents': documents})
    
    # 路由：获取单个文档
    @app.route('/api/documents/<int:doc_id>', methods=['GET'])
    def get_document(doc_id):
        logger.info(f"获取文档 ID: {doc_id}")
        db_manager = get_db_manager()
        document = db_manager.get_document(doc_id)
        if document:
            logger.info(f"成功获取文档 ID: {doc_id}")
            return jsonify({'success': True, 'document': document})
        else:
            logger.warning(f"文档 ID: {doc_id} 不存在")
            return jsonify({'success': False, 'error': '文档不存在'}), 404
    
    # 路由：保存文档
    @app.route('/api/documents', methods=['POST'])
    def save_document():
        data = request.json
        title = data.get('title', '无标题文档')
        content = data.get('content', '')
        doc_id = data.get('id')
        
        logger.info(f"保存文档 - 标题: {title}, ID: {doc_id}")
        db_manager = get_db_manager()
        document_id = db_manager.save_document(title, content, doc_id)
        logger.info(f"文档保存成功 - 新ID: {document_id}")
        return jsonify({'success': True, 'id': document_id})
    
    # 路由：更新文档
    @app.route('/api/documents/<int:doc_id>', methods=['PUT'])
    def update_document(doc_id):
        try:
            data = request.json
            title = data.get('title', '无标题文档')
            content = data.get('content', '')
            
            logger.info(f"更新文档 - ID: {doc_id}, 标题: {title}")
            db_manager = get_db_manager()
            
            # 检查文档是否存在
            document = db_manager.get_document(doc_id)
            if not document:
                logger.warning(f"文档 ID: {doc_id} 不存在")
                return jsonify({'success': False, 'error': '文档不存在'}), 404
            
            # 更新文档
            document_id = db_manager.save_document(title, content, doc_id)
            logger.info(f"文档更新成功 - ID: {document_id}")
            return jsonify({'success': True, 'id': document_id})
        except Exception as e:
            logger.error(f"更新文档处理异常: {str(e)}")
            return jsonify({'success': False, 'error': f'服务器内部错误: {str(e)}'}), 500
    
    # 路由：删除文档
    @app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
    def delete_document(doc_id):
        logger.info(f"删除文档 ID: {doc_id}")
        db_manager = get_db_manager()
        db_manager.delete_document(doc_id)
        logger.info(f"文档 ID: {doc_id} 删除成功")
        return jsonify({'success': True})
    
    # 路由：获取文档历史记录
    @app.route('/api/documents/<int:doc_id>/history', methods=['GET'])
    def get_document_history(doc_id):
        logger.info(f"获取文档历史记录 - 文档 ID: {doc_id}")
        db_manager = get_db_manager()
        history = db_manager.get_document_history(doc_id)
        logger.info(f"成功获取文档 {doc_id} 的历史记录，共 {len(history)} 条记录")
        return jsonify({'success': True, 'history': history})
    
    # 路由：获取AI配置
    @app.route('/api/config', methods=['GET'])
    def get_config():
        logger.info("获取AI配置")
        config_manager = get_config_manager()
        config = config_manager.get_config()
        logger.info("AI配置获取成功")
        return jsonify({'success': True, 'config': config})
    
    # 路由：更新AI配置
    @app.route('/api/config', methods=['POST'])
    def update_config():
        data = request.json
        logger.info("更新AI配置")
        ai_service = get_ai_service()
        config_manager = get_config_manager()
        ai_service.update_config(data)
        config_manager.save_config(data)
        logger.info("AI配置更新成功")
        return jsonify({'success': True})
    
    # 路由：获取所有设置（合并AI配置和应用配置）
    @app.route('/api/settings', methods=['GET'])
    def get_settings():
        logger.info("获取所有设置")
        config_manager = get_config_manager()
        ai_config = config_manager.get_config()
        app_config = config_manager.get_app_config()
        
        # 合并配置
        settings = {
            **ai_config,
            **app_config
        }
        
        logger.info("所有设置获取成功")
        return jsonify({'success': True, 'settings': settings})
    
    # 路由：更新所有设置（合并AI配置和应用配置）
    @app.route('/api/settings', methods=['POST'])
    def update_settings():
        data = request.json
        logger.info("更新所有设置")
        
        # 分离AI配置和应用配置
        ai_config_keys = ['api_key', 'base_url', 'model', 'temperature', 'max_tokens']
        ai_config = {k: v for k, v in data.items() if k in ai_config_keys}
        app_config = {k: v for k, v in data.items() if k not in ai_config_keys}
        
        # 更新AI配置
        if ai_config:
            ai_service = get_ai_service()
            ai_service.update_config(ai_config)
            config_manager = get_config_manager()
            config_manager.save_config(ai_config)
        
        # 更新应用配置
        if app_config:
            config_manager = get_config_manager()
            config_manager.save_app_config(app_config)
        
        logger.info("所有设置更新成功")
        return jsonify({'success': True})
    
    # 路由：测试AI连接
    @app.route('/api/test-connection', methods=['POST'])
    def test_connection():
        try:
            data = request.json
            api_key = data.get('api_key', '')
            base_url = data.get('base_url', '')
            model = data.get('model', '')
            
            logger.info("测试AI连接")
            
            if not api_key:
                logger.warning("测试连接失败 - API密钥为空")
                return jsonify({'success': False, 'error': 'API密钥不能为空'}), 400
            
            # 创建临时AI服务实例进行测试
            temp_config = {
                'api_key': api_key,
                'base_url': base_url,
                'model': model
            }
            temp_ai_service = AIService()
            temp_ai_service.update_config(temp_config)
            
            # 发送测试消息
            test_result = temp_ai_service.chat("测试连接", "")
            
            if test_result.get('success'):
                logger.info("AI连接测试成功")
                return jsonify({'success': True, 'message': '连接成功'})
            else:
                logger.error(f"AI连接测试失败 - 错误: {test_result.get('error')}")
                return jsonify({'success': False, 'error': test_result.get('error', '连接失败')}), 400
                
        except Exception as e:
            logger.error(f"AI连接测试异常: {str(e)}")
            return jsonify({'success': False, 'error': f'连接测试失败: {str(e)}'}), 500

    # 路由：获取应用配置
    @app.route('/api/app-config', methods=['GET'])
    def get_app_config():
        logger.info("获取应用配置")
        config_manager = get_config_manager()
        config = config_manager.get_app_config()
        logger.info("应用配置获取成功")
        return jsonify({'success': True, 'config': config})
    
    # 路由：更新应用配置
    @app.route('/api/app-config', methods=['POST'])
    def update_app_config():
        data = request.json
        logger.info("更新应用配置")
        config_manager = get_config_manager()
        config_manager.save_app_config(data)
        logger.info("应用配置更新成功")
        return jsonify({'success': True})
    
    # 路由：AI对话
    @app.route('/api/chat', methods=['POST'])
    def chat():
        try:
            data = request.json
            message = data.get('message', '')
            context = data.get('context', '')
            
            logger.info(f"AI对话请求 - 消息长度: {len(message)} 字符")
            
            if not message:
                logger.warning("AI对话请求失败 - 消息为空")
                return jsonify({'success': False, 'error': '消息不能为空'}), 400
            
            ai_service = get_ai_service()
            result = ai_service.chat(message, context)
            
            if result.get('success'):
                logger.info("AI对话请求成功")
            else:
                logger.error(f"AI对话请求失败 - 错误: {result.get('error')}")
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"AI对话处理异常: {str(e)}")
            return jsonify({'success': False, 'error': f'服务器内部错误: {str(e)}'}), 500
    
    # 路由：AI编辑
    @app.route('/api/edit', methods=['POST'])
    def edit():
        try:
            data = request.json
            message = data.get('message', '')
            context = data.get('context', '')
            
            logger.info(f"AI编辑请求 - 消息长度: {len(message)} 字符")
            print(f"DEBUG: AI编辑请求 - 消息: {message}, 上下文长度: {len(context)}")
            
            if not message:
                logger.warning("AI编辑请求失败 - 消息为空")
                return jsonify({'success': False, 'error': '消息不能为空'}), 400
            
            ai_service = get_ai_service()
            result = ai_service.chat(message, context)
            print(f"DEBUG: AI服务响应: {result}")
            
            if result.get('success'):
                logger.info("AI编辑请求成功")
            else:
                logger.error(f"AI编辑请求失败 - 错误: {result.get('error')}")
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"AI编辑处理异常: {str(e)}")
            print(f"DEBUG: AI编辑处理异常: {str(e)}")
            return jsonify({'success': False, 'error': f'服务器内部错误: {str(e)}'}), 500
    
    # 路由：渲染Markdown
    @app.route('/api/render', methods=['POST'])
    def render_markdown():
        import markdown
        from markdown.extensions import tables, toc
        
        data = request.json
        content = data.get('content', '')
        
        logger.info(f"渲染Markdown - 内容长度: {len(content)} 字符")
        
        # 配置Markdown扩展（移除代码高亮）
        extensions = [
            'tables',
            'toc',
            'fenced_code'
        ]
        
        # 渲染Markdown
        html = markdown.markdown(content, extensions=extensions)
        
        logger.info("Markdown渲染成功")
        return jsonify({'success': True, 'html': html})
    
    # 路由：上传图片
    @app.route('/api/upload/image', methods=['POST'])
    def upload_image():
        logger.info("收到图片上传请求")
        
        # 确保上传目录存在
        upload_dir = os.path.join(app.static_folder, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        if 'image' not in request.files:
            logger.warning("图片上传失败 - 没有图片文件")
            return jsonify({'success': False, 'error': '没有图片文件'}), 400
        
        file = request.files['image']
        if file.filename == '':
            logger.warning("图片上传失败 - 没有选择文件")
            return jsonify({'success': False, 'error': '没有选择文件'}), 400
        
        # 检查文件类型
        if not file.content_type.startswith('image/'):
            logger.warning(f"图片上传失败 - 文件类型不支持: {file.content_type}")
            return jsonify({'success': False, 'error': '文件类型不支持'}), 400
        
        # 生成唯一文件名
        import uuid
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = str(uuid.uuid4()) + file_ext
        file_path = os.path.join(upload_dir, unique_filename)
        
        # 保存文件
        file.save(file_path)
        logger.info(f"图片保存成功 - 路径: {file_path}")
        
        # 返回文件URL
        file_url = f'/static/uploads/{unique_filename}'
        logger.info(f"图片上传成功 - URL: {file_url}")
        return jsonify({'success': True, 'url': file_url})
    
    # 路由：AI测试页面
    @app.route('/test-ai')
    def test_ai():
        logger.info("访问AI测试页面")
        return send_from_directory(app.static_folder, 'test-ai.html')
    
    # 路由：关闭服务器
    @app.route('/shutdown', methods=['POST'])
    def shutdown():
        logger.info("收到关闭服务器请求")
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            logger.warning("无法使用werkzeug.server.shutdown")
            return jsonify({'success': False, 'error': '不支持关闭操作'}), 400
        
        func()
        logger.info("服务器关闭请求已处理")
        return jsonify({'success': True, 'message': '服务器正在关闭'})
    
    # 路由：获取日志文件列表
    @app.route('/api/logs', methods=['GET'])
    def get_log_files():
        logger.info("获取日志文件列表")
        log_manager = get_log_manager()
        log_files = log_manager.get_log_files()
        logger.info(f"成功获取 {len(log_files)} 个日志文件")
        return jsonify({'success': True, 'log_files': log_files})
    
    # 路由：获取日志内容
    @app.route('/api/logs/<file_name>', methods=['GET'])
    def get_log_content(file_name):
        logger.info(f"获取日志内容 - 文件: {file_name}")
        lines = request.args.get('lines', 100, type=int)
        log_manager = get_log_manager()
        result = log_manager.get_log_content(file_name, lines)
        
        if result['success']:
            logger.info(f"成功获取日志内容 - 文件: {file_name}, 行数: {result['showed_lines']}")
        else:
            logger.error(f"获取日志内容失败 - 文件: {file_name}, 错误: {result['error']}")
        
        return jsonify(result)
    
    # 路由：搜索日志
    @app.route('/api/logs/search', methods=['POST'])
    def search_logs():
        data = request.json
        keyword = data.get('keyword', '')
        file_name = data.get('file_name')
        max_results = data.get('max_results', 100)
        
        logger.info(f"搜索日志 - 关键词: {keyword}, 文件: {file_name}")
        log_manager = get_log_manager()
        result = log_manager.search_logs(keyword, file_name, max_results)
        
        if result['success']:
            logger.info(f"搜索成功 - 找到 {result['total']} 条结果")
        else:
            logger.error(f"搜索失败 - 错误: {result.get('error', '未知错误')}")
        
        return jsonify(result)
    
    # 路由：清空日志
    @app.route('/api/logs/clear', methods=['POST'])
    def clear_logs():
        data = request.json
        file_name = data.get('file_name')
        
        logger.info(f"清空日志 - 文件: {file_name}")
        log_manager = get_log_manager()
        result = log_manager.clear_logs(file_name)
        
        if result['success']:
            logger.info(f"清空日志成功 - {result['message']}")
        else:
            logger.error(f"清空日志失败 - 错误: {result['error']}")
        
        return jsonify(result)
    
    # 路由：删除日志
    @app.route('/api/logs/delete', methods=['POST'])
    def delete_logs():
        data = request.json
        file_name = data.get('file_name')
        
        logger.info(f"删除日志 - 文件: {file_name}")
        log_manager = get_log_manager()
        result = log_manager.delete_logs(file_name)
        
        if result['success']:
            logger.info(f"删除日志成功 - {result['message']}")
        else:
            logger.error(f"删除日志失败 - 错误: {result['error']}")
        
        return jsonify(result)
    
    # 路由：获取版本信息
    @app.route('/api/version', methods=['GET'])
    def get_version():
        logger.info("获取版本信息")
        try:
            # 读取版本配置文件
            version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'version.json')
            if os.path.exists(version_file):
                with open(version_file, 'r', encoding='utf-8') as f:
                    version_info = json.load(f)
                logger.info(f"版本信息获取成功 - 版本: {version_info.get('version', '未知')}")
                return jsonify({'success': True, 'version_info': version_info})
            else:
                # 如果版本文件不存在，返回默认版本
                default_version = {
                    'version': '1.0.0',
                    'build_date': '2023-12-07',
                    'author': 'Markdown Editor Team',
                    'description': '一个简单易用的 Markdown 编辑器，支持实时预览、AI 助手和文档管理。'
                }
                logger.warning("版本配置文件不存在，返回默认版本信息")
                return jsonify({'success': True, 'version_info': default_version})
        except Exception as e:
            logger.error(f"获取版本信息失败: {str(e)}")
            return jsonify({'success': False, 'error': f'获取版本信息失败: {str(e)}'}), 500
    
    # 路由：打包日志
    @app.route('/api/logs/pack', methods=['POST'])
    def pack_logs():
        logger.info("打包日志")
        log_manager = get_log_manager()
        result = log_manager.pack_logs()
        
        if result['success']:
            logger.info(f"打包日志成功 - {result['message']}")
        else:
            logger.error(f"打包日志失败 - 错误: {result['error']}")
        
        return jsonify(result)
    
    return app
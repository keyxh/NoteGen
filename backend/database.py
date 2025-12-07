#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模型
"""

import sqlite3
import json
import os
import logging
from datetime import datetime
from backend.config import Config

# 配置日志
logger = logging.getLogger('app.database')

class DBManager:
    """数据库管理器"""
    
    def __init__(self):
        logger.info("初始化数据库管理器")
        self.db_path = Config.DATABASE_PATH
        self.init_db()
        logger.info(f"数据库管理器初始化完成 - 数据库路径: {self.db_path}")
    
    def init_db(self):
        """初始化数据库"""
        logger.info("初始化数据库")
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 连接数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建文档表
        logger.info("创建文档表")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建历史记录表
        logger.info("创建历史记录表")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS document_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
        )
        ''')
        
        # 提交更改并关闭连接
        conn.commit()
        conn.close()
        
        logger.info("数据库初始化完成")
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def save_document(self, title, content, doc_id=None):
        """保存文档"""
        logger.info(f"保存文档 - 标题: {title}, ID: {doc_id}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if doc_id:
            # 更新现有文档
            logger.info(f"更新现有文档 ID: {doc_id}")
            cursor.execute('''
            UPDATE documents 
            SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            ''', (title, content, doc_id))
            
            # 保存到历史记录
            cursor.execute('''
            INSERT INTO document_history (document_id, content)
            VALUES (?, ?)
            ''', (doc_id, content))
            
            document_id = doc_id
        else:
            # 创建新文档
            logger.info("创建新文档")
            cursor.execute('''
            INSERT INTO documents (title, content)
            VALUES (?, ?)
            ''', (title, content))
            
            document_id = cursor.lastrowid
            
            # 保存到历史记录
            cursor.execute('''
            INSERT INTO document_history (document_id, content)
            VALUES (?, ?)
            ''', (document_id, content))
        
        conn.commit()
        conn.close()
        
        logger.info(f"文档保存成功 - 文档ID: {document_id}")
        return document_id
    
    def get_document(self, doc_id):
        """获取单个文档"""
        logger.info(f"获取文档 - ID: {doc_id}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
        doc = cursor.fetchone()
        
        conn.close()
        
        if doc:
            logger.info(f"文档获取成功 - ID: {doc_id}")
            return {
                'id': doc[0],
                'title': doc[1],
                'content': doc[2],
                'created_at': doc[3],
                'updated_at': doc[4]
            }
        else:
            logger.warning(f"文档不存在 - ID: {doc_id}")
            return None
    
    def get_all_documents(self):
        """获取所有文档"""
        logger.info("获取所有文档列表")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents ORDER BY updated_at DESC')
        docs = cursor.fetchall()
        
        conn.close()
        
        logger.info(f"成功获取文档列表 - 共 {len(docs)} 个文档")
        return [{
            'id': doc[0],
            'title': doc[1],
            'content': doc[2],
            'created_at': doc[3],
            'updated_at': doc[4]
        } for doc in docs]
    
    def delete_document(self, doc_id):
        """删除文档"""
        logger.info(f"删除文档 - ID: {doc_id}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        if deleted:
            logger.info(f"文档删除成功 - ID: {doc_id}")
        else:
            logger.warning(f"文档删除失败 - ID: {doc_id} 不存在")
        
        return deleted
    
    def get_document_history(self, doc_id):
        """获取文档历史记录"""
        logger.info(f"获取文档历史记录 - 文档ID: {doc_id}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM document_history 
        WHERE document_id = ? 
        ORDER BY created_at DESC
        ''', (doc_id,))
        
        history = cursor.fetchall()
        conn.close()
        
        logger.info(f"成功获取文档历史记录 - 文档ID: {doc_id}, 记录数: {len(history)}")
        return [{
            'id': h[0],
            'document_id': h[1],
            'content': h[2],
            'created_at': h[3]
        } for h in history]
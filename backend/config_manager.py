#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
"""

import json
import os
import logging
from backend.config import Config

# 配置日志
logger = logging.getLogger('app.config_manager')

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        logger.info("初始化配置管理器")
        self.config_file = Config.CONFIG_FILE
        self.app_config_file = Config.APP_CONFIG_FILE
        self.ensure_config_exists()
        logger.info(f"配置管理器初始化完成 - 配置文件路径: {self.config_file}")
    
    def ensure_config_exists(self):
        """确保配置文件存在"""
        logger.info("检查配置文件是否存在")
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # 如果配置文件不存在，创建默认配置
        if not os.path.exists(self.config_file):
            logger.info("配置文件不存在，创建默认配置")
            self.save_config(Config.OPENAI_CONFIG)
        else:
            logger.info("配置文件已存在")
            
        # 如果应用配置文件不存在，创建默认应用配置
        if not os.path.exists(self.app_config_file):
            logger.info("应用配置文件不存在，创建默认应用配置")
            self.save_app_config(Config.DEFAULT_APP_CONFIG)
        else:
            logger.info("应用配置文件已存在")
    
    def get_config(self):
        """获取配置"""
        logger.info("获取配置信息")
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info("配置信息获取成功")
                return config
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"配置文件读取失败，使用默认配置: {str(e)}")
            return Config.OPENAI_CONFIG
    
    def save_config(self, config):
        """保存配置"""
        logger.info("保存配置信息")
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            
        logger.info("配置信息保存成功")
        
    def get_app_config(self):
        """获取应用配置"""
        logger.info("获取应用配置信息")
        
        try:
            with open(self.app_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info("应用配置信息获取成功")
                return config
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"应用配置文件读取失败，使用默认配置: {str(e)}")
            return Config.DEFAULT_APP_CONFIG
    
    def save_app_config(self, config):
        """保存应用配置"""
        logger.info("保存应用配置信息")
        
        with open(self.app_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            
        logger.info("应用配置信息保存成功")
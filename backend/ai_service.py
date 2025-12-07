#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI服务模块
"""

import requests
import json
import logging
from backend.config_manager import ConfigManager

# 配置日志
logger = logging.getLogger('app.ai_service')

class AIService:
    """AI服务类"""
    
    def __init__(self):
        logger.info("初始化AI服务")
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        logger.info(f"AI服务初始化完成 - 模型: {self.config.get('model', '未知')}")
    
    def update_config(self, new_config):
        """更新配置"""
        logger.info("更新AI服务配置")
        self.config = new_config
        self.config_manager.save_config(new_config)
        logger.info("AI服务配置更新完成")
    
    def chat(self, message, context=None):
        """与AI对话"""
        logger.info(f"开始AI对话 - 消息长度: {len(message)} 字符")
        
        try:
            # 检查配置是否完整
            if not all(key in self.config for key in ['api_key', 'base_url', 'model']):
                missing_keys = [key for key in ['api_key', 'base_url', 'model'] if key not in self.config]
                error_msg = f"配置不完整，缺少: {', '.join(missing_keys)}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config['api_key']}"
            }
            
            # 构建消息内容
            messages = []
            
            # 添加系统提示和上下文（如果有）
            system_prompt = "你是一个专业的Markdown助手，可以帮助用户生成、编辑和优化Markdown内容。"
            if context:
                system_prompt += f"\n\n当前Markdown内容：\n{context}"
            
            messages.append({"role": "system", "content": system_prompt})
            
            # 添加用户消息
            messages.append({"role": "user", "content": message})
            
            # 请求数据
            data = {
                "model": self.config['model'],
                "messages": messages,
                "temperature": self.config.get('temperature', 0.7),
                "max_tokens": self.config.get('max_tokens', 2000)
            }
            
            timeout = self.config.get('timeout', 30)
            logger.info(f"发送AI请求 - 模型: {self.config['model']}, Base URL: {self.config['base_url']}, 超时: {timeout}秒")
            
            # 发送请求
            response = requests.post(
                f"{self.config['base_url']}/chat/completions",
                headers=headers,
                json=data,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0 and 'message' in result['choices'][0]:
                    response_content = result['choices'][0]['message']['content']
                    logger.info(f"AI对话成功 - 响应长度: {len(response_content)} 字符")
                    return {
                        'success': True,
                        'response': response_content  # 使用 'response' 而不是 'message' 以匹配前端期望
                    }
                else:
                    error_msg = f"API响应格式不正确: {result}"
                    logger.error(error_msg)
                    return {
                        'success': False,
                        'error': error_msg
                    }
            else:
                error_msg = f"API请求失败: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except requests.exceptions.Timeout:
            error_msg = f"请求超时 (超过 {timeout} 秒)"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求错误: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"处理错误: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
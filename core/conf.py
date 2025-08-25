#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全局配置
管理MySQL地址/账号、embedding模型密钥、Qwen2.5-32B接口、0.6阈值等配置
"""

import os

class Config:
    """
    全局配置类
    """

    # 项目根目录配置
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 大模型配置
    LLM_MODEL = "qwen-plus"
    LLM_API_KEY = "sk-0a5ae6123741483cb6a8a1623fe7607f"
    LLM_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # 对话历史配置
    MAX_DIALOGUE_HISTORY = 3

    # 日志配置
    LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
    LOG_FILE_PATH = os.path.join(LOG_DIR, "app.log")
    
    # 确保日志目录存在
    os.makedirs(LOG_DIR, exist_ok=True)

# 创建全局配置实例
config = Config()
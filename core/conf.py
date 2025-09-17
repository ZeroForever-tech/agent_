#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全局配置
管理MySQL地址/账号、embedding模型密钥、Qwen2.5-32B接口、0.6阈值等配置
"""
from dotenv import load_dotenv
import os
import datetime

load_dotenv()
class Config:
    """
    全局配置类
    """

    # 项目根目录配置
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 大模型配置
    LLM_MODEL = os.getenv("LLM_MODEL", "")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_API_URL = os.getenv("LLM_API_URL", "")

    # embedding外部api请求配置
    GET_IP_URL = os.getenv("GET_IP_URL", "")

    # 对话历史配置
    MAX_DIALOGUE_HISTORY = 3

    # 日志配置
    LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
    # 按日期生成日志文件名
    today = datetime.datetime.now().strftime("%Y%m%d")
    LOG_FILE_PATH = os.path.join(LOG_DIR, f"agent_{today}.log")

    # 确保日志目录存在
    os.makedirs(LOG_DIR, exist_ok=True)
# 创建全局配置实例
config = Config()
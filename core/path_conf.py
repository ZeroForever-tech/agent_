#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
路径配置
定义知识库向量缓存路径、日志存储路径等
"""

import os

class PathConfig:
    """
    路径配置类
    """
    
    # 项目根目录
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    
    # 日志存储路径
    LOG_PATH = os.path.join(PROJECT_ROOT, "logs")
    
    # 文档路径
    DOCS_PATH = os.path.join(PROJECT_ROOT, "docs")

# 创建路径配置实例
path_config = PathConfig()

# 确保必要的目录存在
os.makedirs(path_config.KB_VECTOR_CACHE_PATH, exist_ok=True)
os.makedirs(path_config.LOG_PATH, exist_ok=True)
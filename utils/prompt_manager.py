#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
提示词管理器
存储/动态生成Prompt模板
"""

import os
import logging
from typing import List, Optional
from core.conf import config

logger = logging.getLogger(__name__)

class PromptManager:
    """
    提示词管理器类
    """
    
    def __init__(self):
        """
        初始化提示词管理器
        """
        pass
    
    def get_system_prompt_with_key_points(self, key_points: List[str], file_path: Optional[str] = None) -> str:
        """
        获取包含关键点的系统提示词
        
        Args:
            key_points (List[str]): 关键点列表
            file_path (Optional[str]): 提示词模板文件路径，如果未提供则使用默认模板
            
        Returns:
            str: 系统提示词
        """
        # 将关键点列表格式化为字符串
        key_points_str = "\n".join([f"- {point}" for point in key_points])
        
        if file_path and os.path.exists(file_path):
            # 从文件读取模板
            logger.info(f"从文件读取系统提示词模板: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                template = f.read()
            # 将格式化后的字符串传递给模板
            result = template.format(key_points_str=key_points_str)
            logger.info("系统提示词构建完成")
            return result
        else:
            # 使用默认模板
            logger.info("使用默认系统提示词模板")
            default_template = """你是一个智能教学助手，请根据以下关键知识点回答用户的问题：

关键知识点：
{key_points_str}

请基于以上关键知识点，用简洁明了的语言回答用户的问题。回答时请注意：
1. 使用学生容易理解的语言
2. 适当举例说明
3. 回答要准确、简洁"""
            result = default_template.format(key_points_str=key_points_str)
            logger.info("默认系统提示词构建完成")
            return result
    
    def get_fallback_prompt(self, question: str, file_path: Optional[str] = None) -> str:
        """
        获取备用提示词
        
        Args:
            question (str): 用户问题
            file_path (Optional[str]): 提示词模板文件路径，如果未提供则使用默认模板
            
        Returns:
            str: 备用提示词
        """
        if file_path and os.path.exists(file_path):
            # 从文件读取模板
            logger.info(f"从文件读取备用提示词模板: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                template = f.read()
            result = template.format(question=question)
            logger.info("备用提示词构建完成")
            return result
        else:
            # 使用默认模板
            logger.info("使用默认备用提示词模板")
            default_template = """你是一名数学家教，请用简洁的语言回答八年级二次根式问题：{question}
请注意：
1. 回答要准确、简洁
2. 使用学生容易理解的语言
3. 适当举例说明"""
            result = default_template.format(question=question)
            logger.info("默认备用提示词构建完成")
            return result
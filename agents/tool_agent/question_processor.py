#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户问题处理器
处理用户输入的自然语言问题，提取二次根式相关的核心诉求
"""

import re
import logging

logger = logging.getLogger(__name__)

class QuestionProcessor:
    """
    二次根式问题处理器
    """
    
    def __init__(self):
        """
        初始化问题处理器
        """
        pass
    
    def process(self, user_question: str) -> str:
        """
        处理用户问题
        
        Args:
            user_question (str): 用户输入的自然语言问题
            
        Returns:
            str: 处理后的问题
        """
        # 去除问题前后的空格
        processed_question = user_question.strip()
        
        # 去除问题末尾的问号（如果有的话）
        if processed_question.endswith('?') or processed_question.endswith('？'):
            processed_question = processed_question[:-1]
            
        # 简单的关键词提取和规范化
        # 这里可以添加更复杂的自然语言处理逻辑
        processed_question = re.sub(r'\s+', ' ', processed_question)  # 合并多个空格为一个
        
        return processed_question
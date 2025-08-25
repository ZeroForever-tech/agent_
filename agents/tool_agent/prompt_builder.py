#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prompt构建器
根据外部API返回结果构建系统提示词
"""

from utils.prompt_manager import PromptManager
from typing import List, Optional

class PromptBuilder:
    """
    Prompt构建器类
    """
    
    def __init__(self):
        """
        初始化Prompt构建器
        """
        self.prompt_manager = PromptManager()

    
    def build_with_knowledge_and_key_points(self, key_points: List[str], file_path: Optional[str] = None) -> str:
        """
        构建包含关键点信息的系统提示词
        
        Args:
            key_points (List[str]): 关键点列表
            file_path (Optional[str]): 提示词模板文件路径
            
        Returns:
            str: 构建好的系统提示词
        """
        return self.prompt_manager.get_system_prompt_with_key_points(key_points, file_path)
    
    def build_fallback(self, user_question: str, file_path: Optional[str] = None) -> str:
        """
        构建备用提示词（当相似度低于阈值时使用）
        
        Args:
            user_question (str): 用户问题
            file_path (Optional[str]): 提示词模板文件路径
            
        Returns:
            str: 备用提示词
        """
        return self.prompt_manager.get_fallback_prompt(user_question, file_path)
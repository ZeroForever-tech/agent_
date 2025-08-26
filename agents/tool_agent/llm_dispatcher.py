#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
大模型调度器
根据外部API返回结果，触发Qwen Plus调用逻辑
"""

import logging
from llms.qwen_llm import QwenLLM
from core.conf import config
from typing import AsyncGenerator
import traceback

logger = logging.getLogger(__name__)

class LLMDispatcher:
    """
    大模型调度器类
    """
    
    def __init__(self):
        """
        初始化大模型调度器

        """
        # 初始化大模型接口
        self.llm = QwenLLM(config.LLM_API_KEY, config.LLM_API_URL)

    
    def dispatch_with_knowledge(self, system_prompt: str, user_question: str) -> str:
        """
        使用知识库信息调度大模型生成回答
        
        Args:
            system_prompt (str): 包含知识库信息的系统提示词
            user_question (str): 用户问题
            
        Returns:
            str: 大模型生成的回答
        """
        try:
            return self.llm.generate_with_knowledge(system_prompt, user_question)
        except Exception as e:
            logger.error(f"调用大模型时出错: {e}", exc_info=True)
            return "抱歉，我暂时无法回答您的问题，请稍后重试。"
    
    def dispatch_fallback(self, system_prompt: str, user_question: str) -> str:
        """
        使用备用方式调度大模型生成回答
        
        Args:
            system_prompt (str): 系统提示词
            user_question (str): 用户问题
            
        Returns:
            str: 大模型生成的回答
        """
        try:
            return self.llm.generate_fallback(system_prompt, user_question)
        except Exception as e:
            logger.error(f"调用大模型时出错: {e}", exc_info=True)
            return "抱歉，我暂时无法回答您的问题，请稍后重试。"
    
    async def dispatch_with_knowledge_stream(self, system_prompt: str, user_question: str) -> AsyncGenerator[str, None]:
        """
        使用知识库信息调度大模型生成流式回答
        
        Args:
            system_prompt (str): 包含知识库信息的系统提示词
            user_question (str): 用户问题
            
        Yields:
            str: 大模型生成的文本片段
        """
        try:
            async for chunk in self.llm.generate_with_knowledge_stream(system_prompt, user_question):
                yield chunk
        except Exception as e:
            logger.error(f"调用大模型时出错: {e}", exc_info=True)
            yield "抱歉，我暂时无法回答您的问题，请稍后重试。"
    
    async def dispatch_fallback_stream(self, system_prompt: str, user_question: str) -> AsyncGenerator[str, None]:
        """
        使用备用方式调度大模型生成流式回答
        
        Args:
            system_prompt (str): 系统提示词
            user_question (str): 用户问题
            
        Yields:
            str: 大模型生成的文本片段
        """
        try:
            async for chunk in self.llm.generate_fallback_stream(system_prompt, user_question):
                yield chunk
        except Exception as e:
            logger.error(f"调用大模型时出错: {e}", exc_info=True)
            yield "抱歉，我暂时无法回答您的问题，请稍后重试。"
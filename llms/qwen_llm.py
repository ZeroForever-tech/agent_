#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Qwen Plus大模型接口
支持"带知识库Prompt""备用Prompt"两种调用模式
"""

import time
import logging
from openai import OpenAI
from core.conf import config

logger = logging.getLogger(__name__)

class QwenLLM:
    """
    Qwen Plus大模型接口类
    """
    
    def __init__(self, api_key: str, api_url: str):
        """
        初始化大模型接口
        
        Args:
            api_key (str): API密钥（内部部署可能不需要）
            api_url (str): API地址
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_url
        )
        self.model = config.LLM_MODEL
    
    def generate_with_knowledge(self, system_prompt: str, user_question: str) -> str:
        """
        使用带知识库的Prompt调用大模型
        
        Args:
            system_prompt (str): 系统提示词（包含知识库信息）
            user_question (str): 用户问题
            
        Returns:
            str: 大模型生成的回答
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ]
        
        try:
            logger.info("调用大模型generate_with_knowledge方法")
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            answer = response.choices[0].message.content
            elapsed_time = time.time() - start_time
            logger.info(f"大模型回答生成成功，耗时: {elapsed_time:.2f}秒")
            return answer
        except Exception as e:
            logger.error(f"调用大模型时出错: {str(e)}", exc_info=True)
            return f"调用大模型时出错: {str(e)}"
    
    def generate_fallback(self, fallback_prompt: str, user_prompt: str) -> str:
        """
        使用备用Prompt调用大模型
        
        Args:
            fallback_prompt (str): 备用系统提示词
            user_prompt (str): 用户提示词
            
        Returns:
            str: 大模型生成的回答
        """
        messages = [
            {"role": "system", "content": fallback_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            logger.info("调用大模型generate_fallback方法")
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            answer = response.choices[0].message.content
            elapsed_time = time.time() - start_time
            logger.info(f"大模型备用回答生成成功，耗时: {elapsed_time:.2f}秒")
            return answer
        except Exception as e:
            logger.error(f"调用大模型时出错: {str(e)}", exc_info=True)
            return f"调用大模型时出错: {str(e)}"
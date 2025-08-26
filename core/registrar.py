#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
注册器
启动时注册智能体、大模型，确保组件可调用
"""

from agents.tool_agent.question_processor import QuestionProcessor
from agents.tool_agent.prompt_builder import PromptBuilder
from agents.tool_agent.llm_dispatcher import LLMDispatcher
from llms.qwen_llm import QwenLLM
from core.conf import config

class Registrar:
    """
    组件注册器类
    """
    
    def __init__(self):
        """
        初始化注册器
        """
        self.components = {}
    
    def register_component(self, name: str, component):
        """
        注册组件
        
        Args:
            name (str): 组件名称
            component: 组件实例
        """
        self.components[name] = component
    
    def get_component(self, name: str):
        """
        获取已注册的组件
        
        Args:
            name (str): 组件名称
            
        Returns:
            组件实例
        """
        return self.components.get(name)
    
    def register_all_agents(self):
        """
        注册所有智能体
        """
        # 注册sqrt_agent组件
        self.register_component("question_processor", QuestionProcessor())
        self.register_component("prompt_builder", PromptBuilder())
        self.register_component("llm_dispatcher", LLMDispatcher())

    
    def register_llm(self):
        """
        注册大模型
        """
        llm = QwenLLM(config.LLM_API_KEY, config.LLM_API_URL)
        self.register_component("llm", llm)

# 创建全局注册器实例
registrar = Registrar()
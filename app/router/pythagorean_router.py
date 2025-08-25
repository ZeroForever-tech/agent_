#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
勾股定理问询专属路由
定义POST /api/v1/math/pythagorean接口
"""

import time
import logging
import os
from fastapi import APIRouter
from app.schema.math_schema import ChatRequest, ChatResponse
from app.router.shared_math_handler import handle_math_question
from core.conf import config

# 定义提示词文件路径字典
PROMPT_PATHS = {
    "knowledge": os.path.join(config.PROJECT_ROOT, "agents", "pythagorean_agent", "prompt", "system_prompt_with_knowledge.txt"),
    "fallback": os.path.join(config.PROJECT_ROOT, "agents", "pythagorean_agent", "prompt", "system_fallback_prompt.txt")
}

# 创建路由实例
router = APIRouter(prefix="/api/v1/math", tags=["初二下数学"])

@router.post("/pythagorean", response_model=ChatResponse)
async def pythagorean_chat(request: ChatRequest):
    """
    勾股定理问答接口
    
    Args:
        request (ChatRequest): 聊天请求数据
        
    Returns:
        ChatResponse: 包含回答和相关知识点的响应数据
    """
    start_time = time.time()
    logger.info(f"开始处理勾股定理问题: {request.user_question}")
    
    response = await handle_math_question(request, PROMPT_PATHS)
    
    process_time = time.time() - start_time
    logger.info(f"勾股定理问题处理完成，耗时: {process_time:.2f}秒")
    
    return response
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
应用入口
FastAPI启动、加载配置、开启并发
"""

import logging
import uvicorn
from fastapi import FastAPI
from app.router import sqrt_router, agents_router, pythagorean_router, parallelogram_router, linear_function_router, data_analysis_router
from core.registrar import registrar
from core.conf import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE_PATH, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 创建FastAPI应用实例
app = FastAPI(
    title="二次根式智能问答系统",
    description="专门针对八年级数学二次根式内容的智能问答系统",
    version="1.0.0"
)

# 注册路由
app.include_router(sqrt_router.router)
app.include_router(agents_router.router)
app.include_router(pythagorean_router.router)
app.include_router(parallelogram_router.router)
app.include_router(linear_function_router.router)
app.include_router(data_analysis_router.router)

@app.on_event("startup")
async def startup_event():
    """
    应用启动时的初始化操作
    """
    logger.info("应用启动中...")
    # 注册所有组件
    registrar.register_all_agents()
    registrar.register_llm()
    logger.info("应用启动完成")

@app.get("/")
async def root():
    """
    根路径欢迎信息
    
    Returns:
        dict: 包含欢迎信息的字典
    """
    return {"message": "欢迎使用二次根式智能问答系统"}

@app.get("/health")
async def health_check():
    """
    健康检查接口
    
    Returns:
        dict: 包含健康状态的字典
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    # 启动应用
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
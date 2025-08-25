#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智能体管理器
实现请求并发执行，满足"所有请求并发"要求
"""

import asyncio
from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor
import functools

class AgentManager:
    """
    智能体管理器类
    """
    
    def __init__(self, max_workers: int = 10):
        """
        初始化智能体管理器
        
        Args:
            max_workers (int): 线程池最大工作线程数
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def execute_concurrent(self, tasks: list) -> list:
        """
        并发执行任务列表
        
        Args:
            tasks (list): 任务列表
            
        Returns:
            list: 任务执行结果列表
        """
        # 使用asyncio.gather并发执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    def create_task(self, func: Callable, *args, **kwargs) -> asyncio.Task:
        """
        创建异步任务
        
        Args:
            func (Callable): 要执行的函数
            *args: 函数位置参数
            **kwargs: 函数关键字参数
            
        Returns:
            asyncio.Task: 创建的异步任务
        """
        return asyncio.create_task(func(*args, **kwargs))
    
    def create_io_task(self, func: Callable, *args, **kwargs) -> asyncio.Task:
        """
        创建I/O密集型异步任务
        
        Args:
            func (Callable): 要执行的函数
            *args: 函数位置参数
            **kwargs: 函数关键字参数
            
        Returns:
            asyncio.Task: 创建的异步任务
        """
        loop = asyncio.get_event_loop()
        if asyncio.iscoroutinefunction(func):
            return asyncio.create_task(func(*args, **kwargs))
        else:
            return asyncio.create_task(loop.run_in_executor(self.executor, functools.partial(func, *args, **kwargs)))
    
    def create_cpu_task(self, func: Callable, *args, **kwargs) -> asyncio.Future:
        """
        创建CPU密集型异步任务
        
        Args:
            func (Callable): 要执行的函数
            *args: 函数位置参数
            **kwargs: 函数关键字参数
            
        Returns:
            asyncio.Future: 创建的异步Future对象
        """
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(self.executor, functools.partial(func, *args, **kwargs))
    
    async def close(self):
        """
        关闭线程池
        """
        self.executor.shutdown(wait=True)
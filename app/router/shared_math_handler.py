#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
共享的数学问题处理逻辑
用于处理具有相同逻辑但不同配置的数学问题路由
"""

import asyncio
import traceback
import logging
import time
import aiohttp
from app.schema.math_schema import ChatRequest, ChatResponse
from core.registrar import registrar

logger = logging.getLogger(__name__)

async def handle_math_question(request: ChatRequest, prompt_paths: dict) -> ChatResponse:
    """
    处理数学问题的共享逻辑，优化关键路径
    
    关键路径优化:
    1. 使用aiohttp优化网络请求
    2. 并行处理条件分支（获取报告信息和构建备用提示词）
    3. 避免过度工程化，保持代码简洁
    
    Args:
        request (ChatRequest): 聊天请求数据
        prompt_paths (dict): 包含提示词文件路径的字典
        
    Returns:
        ChatResponse: 包含回答和相关知识点的响应数据
    """
    start_time = time.time()
    try:
        logger.info(f"开始处理请求: {request.user_question}")
        
        # 1. 获取注册的组件 (同步操作，但非常快速)
        question_processor = registrar.get_component("question_processor")
        prompt_builder = registrar.get_component("prompt_builder")
        llm_dispatcher = registrar.get_component("llm_dispatcher")
        
        logger.info(f"组件获取状态 - question_processor: {question_processor is not None}")
        logger.info(f"组件获取状态 - prompt_builder: {prompt_builder is not None}")
        logger.info(f"组件获取状态 - llm_dispatcher: {llm_dispatcher is not None}")
        
        # 检查必要组件是否存在
        if not all([question_processor, prompt_builder, llm_dispatcher]):
            logger.warning("组件缺失，返回初始化错误")
            return ChatResponse(
                answer="系统初始化未完成，请稍后重试。",
                related_knowledge=[]
            )
        
        # 2. 处理用户问题 (CPU密集型)
        logger.info("开始处理用户问题")
        processed_question = question_processor.process(request.user_question)
        logger.info(f"问题处理完成: {processed_question}")
        
        # 3. 创建aiohttp客户端会话用于API调用
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # 4. 获取课程信息 (I/O密集型)
            logger.info("开始获取课程信息")
            courses_response = await fetch_courses(session, processed_question)
            logger.info(f"课程信息获取完成，状态码: {courses_response.status}")
            
            if courses_response.status != 200:
                logger.warning(f"课程信息获取失败，状态码: {courses_response.status}")
                # 如果API调用失败，使用备用方式
                courses_response.close()
                
                # 构建备用提示词 (CPU密集型)
                fallback_prompt = prompt_builder.build_fallback(processed_question, prompt_paths["fallback"])
                
                # 调用备用大模型 (CPU密集型)
                answer = llm_dispatcher.dispatch_fallback(fallback_prompt, processed_question)
                
                logger.info(f"使用备用方式生成回答: {answer}")
                total_time = time.time() - start_time
                logger.info(f"请求处理完成，总耗时: {total_time:.2f}秒")
                return ChatResponse(
                    answer=answer,
                    related_knowledge=[]
                )
            
            # 5. 解析课程数据 (CPU密集型)
            courses_data = await courses_response.json()
            courses_response.close()
            logger.info(f"课程数据解析完成: {courses_data}")
            
            # 检查是否有匹配的课程
            if not courses_data.get("data"):
                logger.info("未找到匹配的课程数据")
                # 如果没有匹配的课程，使用备用方式
                
                # 构建备用提示词 (CPU密集型)
                fallback_prompt = prompt_builder.build_fallback(processed_question, prompt_paths["fallback"])
                
                # 调用备用大模型 (CPU密集型)
                answer = llm_dispatcher.dispatch_fallback(fallback_prompt, processed_question)
                
                logger.info(f"使用备用方式生成回答: {answer}")
                total_time = time.time() - start_time
                logger.info(f"请求处理完成，总耗时: {total_time:.2f}秒")
                return ChatResponse(
                    answer=answer,
                    related_knowledge=[]
                )
            
            # 获取第一个匹配的课程
            course_info = courses_data["data"][0]
            course_uuid = course_info.get("course_uuid", "")
            logger.info(f"获取到课程信息，course_uuid: {course_uuid}")
            
            # 6. 并行处理条件分支：获取报告信息和构建备用提示词
            logger.info("开始并行获取报告信息和构建备用提示词")
            # 创建并行任务
            reports_task = asyncio.create_task(fetch_reports(session, course_uuid, processed_question))
            fallback_task = asyncio.create_task(build_fallback_prompt(prompt_builder, processed_question, prompt_paths["fallback"]))
            
            # 并发执行
            reports_response, fallback_prompt = await asyncio.gather(reports_task, fallback_task)
            logger.info(f"报告信息获取完成，状态码: {reports_response.status}")
            
            if reports_response.status != 200:
                logger.warning(f"报告信息获取失败，状态码: {reports_response.status}")
                # 如果API调用失败，使用备用方式
                reports_response.close()
                
                # 调用备用大模型 (CPU密集型)
                answer = llm_dispatcher.dispatch_fallback(fallback_prompt, processed_question)
                
                logger.info(f"使用备用方式生成回答: {answer}")
                total_time = time.time() - start_time
                logger.info(f"请求处理完成，总耗时: {total_time:.2f}秒")
                return ChatResponse(
                    answer=answer,
                    related_knowledge=[]
                )
            
            # 7. 解析报告数据 (CPU密集型)
            reports_data = await reports_response.json()
            reports_response.close()
            logger.info(f"报告数据解析完成: {reports_data}")
            
            # 8. 构建related_knowledge数据
            related_knowledge = []
            answer = ""
            
            if reports_data.get("data"):
                logger.info("找到报告数据，开始构建相关知识点")
                # 如果有匹配的报告，使用报告信息
                report_info = reports_data["data"][0]
                
                # 构建related_knowledge项
                related_knowledge_item = {
                    "resource_name": course_info.get("resource_name", ""),
                    "file_name": course_info.get("file_name", ""),
                    "video_link": course_info.get("video_link", ""),
                    "video_summary": course_info.get("video_summary", ""),
                    "start_time": report_info.get("start_time", ""),
                    "end_time": report_info.get("end_time", ""),
                    "duration": report_info.get("duration", "")
                }
                related_knowledge.append(related_knowledge_item)
                logger.info(f"相关知识点构建完成: {related_knowledge_item}")
                
                # 构建包含key_points的系统提示词 (CPU密集型)
                key_points = report_info.get("key_points", [])
                logger.info(f"获取到关键点: {key_points}")
                system_prompt = prompt_builder.build_with_knowledge_and_key_points(key_points, prompt_paths["knowledge"])
                logger.info("提示词构建完成")
                
                # 调用大模型生成回答 (CPU密集型)
                logger.info("开始调用大模型生成回答")
                answer = llm_dispatcher.dispatch_with_knowledge(system_prompt, processed_question)
                logger.info(f"大模型回答生成完成: {answer}")
            else:
                logger.info("未找到报告数据，使用备用方式")
                # 如果没有匹配的报告，使用备用方式
                answer = llm_dispatcher.dispatch_fallback(fallback_prompt, processed_question)
                logger.info(f"使用备用方式生成回答: {answer}")
                related_knowledge = []
            
            # 9. 返回结果
            logger.info("处理完成，返回结果")
            total_time = time.time() - start_time
            logger.info(f"请求处理完成，总耗时: {total_time:.2f}秒")
            return ChatResponse(
                answer=answer,
                related_knowledge=related_knowledge
            )
    except Exception as e:
        # 全局异常处理
        logger.error(f"处理请求时发生错误: {e}", exc_info=True)
        total_time = time.time() - start_time
        logger.info(f"请求处理异常结束，总耗时: {total_time:.2f}秒")
        return ChatResponse(
            answer="系统出现错误，请稍后重试。",
            related_knowledge=[]
        )

# 异步辅助函数
async def fetch_courses(session, processed_question):
    """异步获取课程信息"""
    try:
        logger.info(f"异步获取课程信息: {processed_question}")
        courses_api_url = f"http://106.227.68.33:8849/api/v1/recommendation/rag/search/courses?query={processed_question}&top_k=1"
        logger.info(f"课程API URL: {courses_api_url}")
        result = await session.get(courses_api_url)
        logger.info(f"课程API响应状态码: {result.status}")
        return result
    except Exception as e:
        logger.error(f"获取课程信息时发生错误: {e}", exc_info=True)
        raise

async def fetch_reports(session, course_uuid, processed_question):
    """异步获取报告信息"""
    try:
        logger.info(f"异步获取报告信息: course_uuid={course_uuid}, question={processed_question}")
        reports_api_url = f"http://106.227.68.33:8849/api/v1/recommendation/rag/search/reports/{course_uuid}?query={processed_question}&top_k=1"
        logger.info(f"报告API URL: {reports_api_url}")
        result = await session.get(reports_api_url)
        logger.info(f"报告API响应状态码: {result.status}")
        return result
    except Exception as e:
        logger.error(f"获取报告信息时发生错误: {e}", exc_info=True)
        raise

async def build_fallback_prompt(prompt_builder, processed_question, fallback_path):
    """构建备用提示词"""
    try:
        logger.info("构建备用提示词")
        result = prompt_builder.build_fallback(processed_question, fallback_path)
        logger.info("备用提示词构建完成")
        return result
    except Exception as e:
        logger.error(f"构建备用提示词时发生错误: {e}", exc_info=True)
        raise
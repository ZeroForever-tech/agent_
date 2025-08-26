#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
共享的数学问题处理逻辑
用于处理具有相同逻辑但不同配置的数学问题路由
"""

import requests
import logging
import time
import json
from app.schema.math_schema import ChatRequest, ChatResponse
from core.registrar import registrar
from core.conf import config
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, Dict, Any

logger = logging.getLogger(__name__)

async def handle_math_question(request: ChatRequest, prompt_paths: dict) -> ChatResponse:
    """
    处理数学问题的共享逻辑
    
    Args:
        request (ChatRequest): 聊天请求数据
        prompt_paths (dict): 包含提示词文件路径的字典
        
    Returns:
        ChatResponse: 包含回答和相关知识点的响应数据
    """
    start_time = time.time()
    try:
        logger.info(f"开始处理请求: {request.user_question}")
        
        # 获取注册的组件
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
        
        # 1. 处理用户问题
        logger.info("开始处理用户问题")
        processed_question = question_processor.process(request.user_question)
        logger.info(f"问题处理完成: {processed_question}")
        
        # 2. 调用外部推荐系统API获取课程信息
        # GET /api/v1/recommendation/rag/search/courses?query={查询字符串}&top_k=1
        logger.info("开始获取课程信息")
        courses_api_url = config.GET_IP_URL + f"/api/v1/recommendation/rag/search/courses?query={processed_question}&top_k=1"
        courses_response = requests.get(courses_api_url)
        logger.info(f"课程信息获取完成，状态码: {courses_response.status_code}")
        
        if courses_response.status_code != 200:
            # 如果API调用失败，使用备用方式
            logger.warning(f"课程信息获取失败，状态码: {courses_response.status_code}")
            fallback_prompt = prompt_builder.build_fallback(processed_question, prompt_paths["fallback"])
            answer = llm_dispatcher.dispatch_fallback(fallback_prompt, processed_question)
            logger.info(f"使用备用方式生成回答: {answer}")
            total_time = time.time() - start_time
            logger.info(f"请求处理完成，总耗时: {total_time:.2f}秒")
            return ChatResponse(
                answer=answer,
                related_knowledge=[]
            )
        
        courses_data = courses_response.json()
        logger.info(f"课程数据解析完成: {courses_data}")
        
        # 检查是否有匹配的课程
        if not courses_data.get("data"):
            # 如果没有匹配的课程，使用备用方式
            logger.info("未找到匹配的课程数据")
            fallback_prompt = prompt_builder.build_fallback(processed_question, prompt_paths["fallback"])
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
        course_uuid = course_info["course_uuid"]
        logger.info(f"获取到课程信息，course_uuid: {course_uuid}")
        
        # 3. 调用外部推荐系统API获取报告信息
        # GET /api/v1/recommendation/rag/search/reports/{course_id}?query={查询字符串}&top_k=1
        logger.info("开始获取报告信息")
        reports_api_url = config.GET_IP_URL + f"/api/v1/recommendation/rag/search/reports/{course_uuid}?query={processed_question}&top_k=1"
        reports_response = requests.get(reports_api_url)
        logger.info(f"报告信息获取完成，状态码: {reports_response.status_code}")
        
        if reports_response.status_code != 200:
            # 如果API调用失败，使用备用方式
            logger.warning(f"报告信息获取失败，状态码: {reports_response.status_code}")
            fallback_prompt = prompt_builder.build_fallback(processed_question, prompt_paths["fallback"])
            answer = llm_dispatcher.dispatch_fallback(fallback_prompt, processed_question)
            logger.info(f"使用备用方式生成回答: {answer}")
            total_time = time.time() - start_time
            logger.info(f"请求处理完成，总耗时: {total_time:.2f}秒")
            return ChatResponse(
                answer=answer,
                related_knowledge=[]
            )
        
        reports_data = reports_response.json()
        logger.info(f"报告数据解析完成: {reports_data}")
        
        # 构建related_knowledge数据
        related_knowledge = []
        if reports_data.get("data"):
            # 如果有匹配的报告，使用报告信息
            report_info = reports_data["data"][0]
            
            # 构建related_knowledge项
            related_knowledge_item = {
                "resource_name": course_info["resource_name"],
                "file_name": course_info["file_name"],
                "video_link": course_info["video_link"],
                "video_summary": course_info["video_summary"],
                "start_time": report_info["start_time"],
                "end_time": report_info["end_time"],
                "duration": report_info["duration"]
            }
            related_knowledge.append(related_knowledge_item)
            logger.info(f"相关知识点构建完成: {related_knowledge_item}")
            
            # 构建包含key_points的系统提示词
            key_points = report_info.get("key_points", [])
            logger.info(f"获取到关键点: {key_points}")
            system_prompt = prompt_builder.build_with_knowledge_and_key_points(key_points, prompt_paths["knowledge"])
            logger.info("提示词构建完成")
            
            # 调用大模型生成回答
            logger.info("开始调用大模型生成回答")
            answer = llm_dispatcher.dispatch_with_knowledge(system_prompt, processed_question)
            logger.info(f"大模型回答生成完成: {answer}")
        else:
            # 如果没有匹配的报告，使用备用方式
            logger.info("未找到报告数据，使用备用方式")
            fallback_prompt = prompt_builder.build_fallback(processed_question, prompt_paths["fallback"])
            answer = llm_dispatcher.dispatch_fallback(fallback_prompt, processed_question)
            logger.info(f"使用备用方式生成回答: {answer}")
            related_knowledge = []
        
        # 4. 返回结果
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


async def handle_math_question_stream(request: ChatRequest, prompt_paths: dict) -> StreamingResponse:
    """
    处理数学问题并以SSE流式方式返回结果
    
    Args:
        request (ChatRequest): 聊天请求数据
        prompt_paths (dict): 包含提示词文件路径的字典
        
    Returns:
        StreamingResponse: SSE流式响应
    """
    return StreamingResponse(
        stream_math_question_handler(request, prompt_paths),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )


async def stream_math_question_handler(request: ChatRequest, prompt_paths: dict) -> AsyncGenerator[str, None]:
    """
    流式处理数学问题的生成器函数
    
    Args:
        request (ChatRequest): 聊天请求数据
        prompt_paths (dict): 包含提示词文件路径的字典
        
    Yields:
        str: SSE格式的数据片段
    """
    try:
        logger.info(f"开始流式处理请求: {request.user_question}")
        
        # 获取注册的组件
        question_processor = registrar.get_component("question_processor")
        prompt_builder = registrar.get_component("prompt_builder")
        llm_dispatcher = registrar.get_component("llm_dispatcher")
        
        # 检查必要组件是否存在
        if not all([question_processor, prompt_builder, llm_dispatcher]):
            yield f"data: {json.dumps({'type': 'error', 'data': '系统初始化未完成，请稍后重试。'})}\n\n"
            return
        
        # 1. 处理用户问题
        logger.info("开始处理用户问题")
        processed_question = question_processor.process(request.user_question)
        logger.info(f"问题处理完成: {processed_question}")
        
        
        # 2. 调用外部推荐系统API获取课程信息
        # GET /api/v1/recommendation/rag/search/courses?query={查询字符串}&top_k=1
        logger.info("开始获取课程信息")
        courses_api_url = config.GET_IP_URL + f"/api/v1/recommendation/rag/search/courses?query={processed_question}&top_k=1"
        courses_response = requests.get(courses_api_url)
        logger.info(f"课程信息获取完成，状态码: {courses_response.status_code}")
        
        if courses_response.status_code != 200:
            # 如果API调用失败，使用备用方式
            logger.warning(f"课程信息获取失败，状态码: {courses_response.status_code}")
            fallback_prompt = prompt_builder.build_fallback(processed_question, prompt_paths["fallback"])
            
            # 调用备用大模型 (CPU密集型) 并流式返回
            
            async for chunk in llm_dispatcher.dispatch_fallback_stream(fallback_prompt, processed_question):
                yield f"data: {json.dumps({'type': 'answer_chunk', 'data': chunk})}\n\n"
            
            yield f"data: {json.dumps({'type': 'complete', 'data': {'related_knowledge': []}})}\n\n"
            return
        
        courses_data = courses_response.json()
        logger.info(f"课程数据解析完成: {courses_data}")
        
        
        # 检查是否有匹配的课程
        if not courses_data.get("data"):
            # 如果没有匹配的课程，使用备用方式
            logger.info("未找到匹配的课程数据")
            fallback_prompt = prompt_builder.build_fallback(processed_question, prompt_paths["fallback"])

            # 调用备用大模型 (CPU密集型) 并流式返回
            async for chunk in llm_dispatcher.dispatch_fallback_stream(fallback_prompt, processed_question):
                yield f"data: {json.dumps({'type': 'answer_chunk', 'data': chunk})}\n\n"
            
            yield f"data: {json.dumps({'type': 'complete', 'data': {'related_knowledge': []}})}\n\n"
            return
        
        # 获取第一个匹配的课程
        course_info = courses_data["data"][0]
        course_uuid = course_info["course_uuid"]
        logger.info(f"获取到课程信息，course_uuid: {course_uuid}")
        
        
        # 3. 调用外部推荐系统API获取报告信息
        # GET /api/v1/recommendation/rag/search/reports/{course_id}?query={查询字符串}&top_k=1
        logger.info("开始获取报告信息")
        reports_api_url = config.GET_IP_URL + f"/api/v1/recommendation/rag/search/reports/{course_uuid}?query={processed_question}&top_k=1"
        reports_response = requests.get(reports_api_url)
        logger.info(f"报告信息获取完成，状态码: {reports_response.status_code}")
        
        if reports_response.status_code != 200:
            # 如果API调用失败，使用备用方式
            logger.warning(f"报告信息获取失败，状态码: {reports_response.status_code}")
            fallback_prompt = prompt_builder.build_fallback(processed_question, prompt_paths["fallback"])

            # 调用备用大模型 (CPU密集型) 并流式返回
            async for chunk in llm_dispatcher.dispatch_fallback_stream(fallback_prompt, processed_question):
                yield f"data: {json.dumps({'type': 'answer_chunk', 'data': chunk})}\n\n"
            
            yield f"data: {json.dumps({'type': 'complete', 'data': {'related_knowledge': []}})}\n\n"
            return
        
        reports_data = reports_response.json()
        logger.info(f"报告数据解析完成: {reports_data}")
        
        # 发送报告数据
        
        
        # 构建related_knowledge数据
        related_knowledge = []
        if reports_data.get("data"):
            # 如果有匹配的报告，使用报告信息
            report_info = reports_data["data"][0]
            
            # 构建related_knowledge项
            related_knowledge_item = {
                "resource_name": course_info["resource_name"],
                "file_name": course_info["file_name"],
                "video_link": course_info["video_link"],
                "video_summary": course_info["video_summary"],
                "start_time": report_info["start_time"],
                "end_time": report_info["end_time"],
                "duration": report_info["duration"]
            }
            related_knowledge.append(related_knowledge_item)
            logger.info(f"相关知识点构建完成: {related_knowledge_item}")
            
            # 发送相关知识点
            
            # 构建包含key_points的系统提示词
            key_points = report_info.get("key_points", [])
            logger.info(f"获取到关键点: {key_points}")
            system_prompt = prompt_builder.build_with_knowledge_and_key_points(key_points, prompt_paths["knowledge"])
            logger.info("提示词构建完成")
            
            
            # 调用大模型生成回答 (CPU密集型) 并流式返回
            logger.info("开始调用大模型生成回答")
            
            async for chunk in llm_dispatcher.dispatch_with_knowledge_stream(system_prompt, processed_question):
                yield f"data: {json.dumps({'type': 'answer_chunk', 'data': chunk})}\n\n"
            
            logger.info(f"大模型回答生成完成")
        else:
            # 如果没有匹配的报告，使用备用方式
            logger.info("未找到报告数据，使用备用方式")
            fallback_prompt = prompt_builder.build_fallback(processed_question, prompt_paths["fallback"])

            async for chunk in llm_dispatcher.dispatch_fallback_stream(fallback_prompt, processed_question):
                yield f"data: {json.dumps({'type': 'answer_chunk', 'data': chunk})}\n\n"
            
            logger.info(f"使用备用方式生成回答")
            related_knowledge = []
        
        # 4. 发送完成信号
        logger.info("流式处理完成，发送完成信号")
        yield f"data: {json.dumps({'type': 'complete', 'data': {'related_knowledge': related_knowledge}})}\n\n"
    except Exception as e:
        # 全局异常处理
        logger.error(f"处理请求时发生错误: {e}", exc_info=True)
        yield f"data: {json.dumps({'type': 'error', 'data': '系统出现错误，请稍后重试。'})}\n\n"
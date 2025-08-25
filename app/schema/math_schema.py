#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
聊天交互模型
定义请求和响应的数据模型
"""

from pydantic import BaseModel
from typing import List, Dict, Any

class ChatRequest(BaseModel):
    """
    聊天请求模型
    用于接收用户的问题
    """
    user_question: str
    
    class Config:
        # 示例数据仅用于API文档展示
        schema_extra = {
            "example": {
                "user_question": "什么是二次根式？"
            }
        }

class RelatedKnowledgeItem(BaseModel):
    """
    相关知识点项模型
    """
    resource_name: str
    file_name: str
    video_link: str
    video_summary: str
    start_time: str
    end_time: str
    duration: str

class ChatResponse(BaseModel):
    """
    聊天响应模型
    用于返回AI生成的答案和相关知识点
    """
    answer: str
    related_knowledge: List[RelatedKnowledgeItem]
    
    class Config:
        # 示例数据仅用于API文档展示
        schema_extra = {
            "example": {
                "answer": "二次根式是形如√a（a≥0）的式子。",
                "related_knowledge": [
                    {
                        "resource_name": "初中初二下数学",
                        "file_name": "二次根式（一）二次根式的定义",
                        "video_link": "https://vod.jxeduyun.com/view/G8/SX/RJB/20200211/G8_SX_RJB_20200211_2816b04dac424d1db4885e362b5266dd.mp4",
                        "video_summary": "本节课介绍了分数加法的概念与运算方法，并强调了常见易错点及其纠正。",
                        "start_time": "00:05:30",
                        "end_time": "00:15:45",
                        "duration": "10:15"
                    }
                ]
            }
        }
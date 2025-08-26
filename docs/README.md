# 二次根式智能问答系统

## 项目简介

本项目是一个专门针对八年级数学二次根式内容的智能问答系统。用户可以通过自然语言提问，系统将自动分析问题并给出准确的回答。

## 技术架构

- **Web框架**: FastAPI
- **数据验证**: Pydantic
- **大模型**: Qwen2.5-32B
- **向量模型**: text-embedding-3-small
- **数据库**: MySQL

## API接口文档

### 二次根式问答接口

#### 基本信息

- **路径**: `/api/v1/math/sqrt/chat`
- **方法**: POST
- **标签**: 二次根式问答

#### 请求参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| user_question | string | 是 | 用户提出的问题 |

#### 请求示例

```json
{
  "user_question": "什么是二次根式？"
}
```

#### 响应参数

| 参数名 | 类型 | 描述 |
|--------|------|------|
| answer | string | 系统生成的回答 |
| related_knowledge | array | 相关知识点列表 |

#### 响应示例

```json
{
  "answer": "二次根式是形如√a（a≥0）的式子，其中a叫做被开方数。",
  "related_knowledge": [
    ["八年级数学", "二次根式的定义"],
    ["八年级数学", "二次根式有意义的条件"]
  ]
}
```

#### 错误码

| 错误码 | 描述 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 500 | 服务器内部错误 |

## 调用示例

### Python示例

```python
import requests

url = "http://localhost:8000/api/v1/math/sqrt/chat"
data = {"user_question": "如何化简二次根式？"}

response = requests.post(url, json=data)
print(response.json())
```

### JavaScript示例

```javascript
fetch('http://localhost:8000/api/v1/math/sqrt/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({user_question: "如何化简二次根式？"})
})
.then(response => response.json())
.then(data => console.log(data));
```

## 部署说明

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 配置环境变量：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件填入相应配置
   ```

3. 启动服务：
   ```bash
   python main.py
   ```

## 项目结构

```
agent_/
├── agents/                 # 智能体核心目录
│   ├── sqrt_agent/         # 二次根式专属问询智能体
│   └── tool_agent/         # 工具智能体
├── app/                    # 应用层
│   ├── router/             # API路由
│   └── schema/             # 数据模型
├── core/                   # 核心配置
├── llms/                   # 大模型接口层
├── kb/                     # 知识库专属目录
├── utils/                  # 工具类
└── docs/                   # 文档目录
```
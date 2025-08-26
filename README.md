# 智能数学教学助手系统

## 项目简介

这是一个基于 FastAPI 构建的 AI Agent 系统，旨在通过多个专业 Agent 协作完成初中数学教学任务。系统支持二次根式、勾股定理、平行四边形、一次函数和数据分析等多个数学领域的智能问答。

## 功能特性

- **多 Agent 协作架构**：支持多个数学领域的专业智能体
- **智能问答系统**：基于大语言模型的智能问答能力
- **知识库集成**：与外部推荐系统集成，获取课程和知识点信息
- **模块化设计**：便于扩展新领域和新功能
- **RESTful API**：提供标准的 HTTP 接口

## 技术架构

- **后端框架**：FastAPI v0.68.0
- **大语言模型**：Qwen Plus（通过阿里云 DashScope API）
- **向量处理**：scikit-learn v1.0.0, numpy v1.21.0
- **HTTP 请求**：requests v2.25.1
- **配置管理**：python-dotenv v0.18.0
- **运行时**：uvicorn v0.15.0

## 项目结构

```
.
├── agents/                    # 智能体模块
│   ├── sqrt_agent/           # 二次根式智能体
│   ├── pythagorean_agent/    # 勾股定理智能体
│   ├── parallelogram_agent/  # 平行四边形智能体
│   ├── linear_function_agent/ # 一次函数智能体
│   ├── data_analysis_agent/  # 数据分析智能体
│   └── tool_agent/           # 工具智能体
├── app/                      # 应用层
│   ├── router/               # 路由模块
│   └── schema/               # 数据模型
├── core/                     # 核心配置
├── llms/                     # 大语言模型接口
├── utils/                    # 工具模块
├── main.py                   # 应用入口
└── requirements.txt          # 依赖列表
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行项目

```bash
# 方式一：直接运行
python main.py

# 方式二：使用 uvicorn
uvicorn main:app --reload
```

项目将在 `http://localhost:8000` 启动。

## API 接口

### 智能体信息接口

- `GET /api/v1/agents` - 获取所有智能体信息

### 数学问答接口

- `POST /api/v1/math/sqrt` - 二次根式问答
- `POST /api/v1/math/pythagorean` - 勾股定理问答
- `POST /api/v1/math/parallelogram` - 平行四边形问答
- `POST /api/v1/math/linear_function` - 一次函数问答
- `POST /api/v1/math/data_analysis` - 数据分析问答

### 请求示例

```bash
curl -X POST "http://localhost:8000/api/v1/math/sqrt" \
     -H "Content-Type: application/json" \
     -d '{"user_question": "什么是二次根式？"}'
```

### 健康检查接口

- `GET /health` - 系统健康状态检查

## 配置说明

系统配置位于 `core/conf.py` 文件中：

- **大语言模型配置**：
  - 模型
  - API 密钥
  - API URL

## 提示词管理

每个智能体都有独立的提示词模板文件，位于对应智能体目录下的 `prompt/` 文件夹中：

- `system_prompt_with_knowledge.txt` - 带知识点的系统提示词
- `system_fallback_prompt.txt` - 备用提示词

## 开发指南

### 添加新的数学领域智能体

1. 在 `agents/` 目录下创建新的智能体文件夹
2. 在 `app/router/` 目录下创建对应的路由文件
3. 在路由文件中使用 `shared_math_handler.handle_math_question` 共享处理逻辑
4. 在 `main.py` 中注册新的路由
5. 在 `app/router/__init__.py` 中添加导入

### 自定义提示词

修改对应智能体目录下 `prompt/` 文件夹中的文本文件即可自定义提示词模板。

## 文档

- API 文档：`http://localhost:8000/docs`
- ReDoc 文档：`http://localhost:8000/redoc`
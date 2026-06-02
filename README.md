# LLM-Study

基于 LangChain Agent 的 AI 服务项目，提供 RESTful API 接口。

## 启动服务

```bash
python main.py
```

服务默认启动在 http://localhost:8080

## API 文档

启动后访问 http://localhost:8080/docs 查看 Swagger 文档

### 接口列表

| 方法   | 路径                  | 说明                 |
|--------|-----------------------|----------------------|
| POST   | /api/chat/            | 聊天接口（调用 Agent）|
| GET    | /api/weather/         | 查询天气             |
| POST   | /api/clothing/note    | 穿衣建议             |
| GET    | /health               | 健康检查             |

## 项目结构

```
LLM-STUDY/
├── api/                    # API 层
│   ├── __init__.py
│   ├── server.py           # FastAPI 应用入口
│   ├── models/             # 请求/响应模型
│   │   ├── __init__.py
│   │   ├── requests.py
│   │   └── responses.py
│   └── routes/             # 路由模块（按领域拆分）
│       ├── __init__.py
│       ├── chat.py
│       ├── weather.py
│       └── clothing.py
├── config/                 # 配置层
│   ├── __init__.py
│   └── settings.py
├── core/                   # 核心业务层
│   ├── __init__.py
│   ├── agent.py
│   └── llm.py
├── skills/                 # Agent 工具
│   ├── __init__.py
│   ├── skill1_get_weather.py
│   └── skill2_get_temp_note.py
├── main.py                 # 启动入口
├── requirements.txt
└── .env / .env.*           # 环境变量配置
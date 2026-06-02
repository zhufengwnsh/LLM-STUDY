"""FastAPI 应用组装，注册所有路由"""

from fastapi import FastAPI
from api.routes import chat, weather, clothing

app = FastAPI(
    title="LLM-Study API",
    description="基于 LangChain Agent 的 AI 服务接口",
    version="1.0.0"
)

# 注册路由
app.include_router(chat.router)
app.include_router(weather.router)
app.include_router(clothing.router)


@app.get("/health", tags=["System"])
def health_check():
    """健康检查"""
    return {"status": "ok", "service": "LLM-Study API"}
"""项目入口：启动所有 HTTP 服务（FastAPI + Uvicorn）"""

import uvicorn
from api.server import app
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

if __name__ == "__main__":
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=8080,
        reload=False
    )
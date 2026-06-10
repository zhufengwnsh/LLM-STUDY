import uvicorn
from api.server import app
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
import logging
from langchain_core.globals import set_debug, set_verbose

# 开启全量DEBUG日志
set_debug(True)    # 打印完整：prompt、LLM入参、LLM原始返回、工具入参、工具返回值
set_verbose(False)
mcp = FastApiMCP(
    app,
    # 可选配置：只暴露部分接口、修改描述
    include_operations=["get_weather_api_weather__get", "clothing_note_api_clothing_note_post", "get_weather_api_city__get"]
)
# 2. 将MCP服务挂载到FastAPI，访问地址：http://127.0.0.1:8080/mcp
mcp.mount_http()

if __name__ == "__main__":
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )
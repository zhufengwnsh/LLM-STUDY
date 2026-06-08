"""聊天相关路由 - 将 main.py 的逻辑封装为 HTTP POST 接口"""

from fastapi import APIRouter
from core.agent_local_tools import skillAgent
from core.agent_local_mcp_lazy import lazyMcpAgent
from core.agent_local_mcp import mcpAgent
from api.models.requests import ChatRequest
from api.models.responses import ApiResponse

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/mcp/lazy", response_model=ApiResponse)
def chat(req: ChatRequest):
    """
    聊天接口：接收用户消息，调用 LangChain Agent 返回回答
    调用MCP服务
    请求体: {"content": "北京今天多少度？穿什么衣服？"}
    """
    print(f"调用聊天接口[lazy-mcp],content:{req.content}")
    response = lazyMcpAgent.invoke({
        "messages": [
            {"role": "user", "content": req.content}
        ]
    })

    # 从 response 中提取最终回答
    answer = response.get("output", str(response))
    return ApiResponse(data=answer)

@router.post("/local", response_model=ApiResponse)
def chat(req: ChatRequest):
    """
    聊天接口：接收用户消息，调用 LangChain Agent 返回回答
    调用本地skill
    请求体: {"content": "北京今天多少度？穿什么衣服？"}
    """
    print(f"调用聊天接口[本地skill],content:{req.content}")
    response = skillAgent.invoke({
        "messages": [
            {"role": "user", "content": req.content}
        ]
    })
    # 从 response 中提取最终回答
    answer = response.get("output", str(response))
    return ApiResponse(data=answer)


@router.post("/mcp", response_model=ApiResponse)
def chat(req: ChatRequest):
    """
    聊天接口：接收用户消息，调用 LangChain Agent 返回回答
    调用MCP服务
    请求体: {"content": "北京今天多少度？穿什么衣服？"}
    """
    print(f"调用聊天接口[mcp],content:{req.content}")
    agent = mcpAgent()
    response = agent.invoke({
        "messages": [
            {"role": "user", "content": req.content}
        ]
    })

    # 从 response 中提取最终回答
    answer = response.get("output", str(response))
    return ApiResponse(data=answer)
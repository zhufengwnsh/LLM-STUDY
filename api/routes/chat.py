"""聊天相关路由 - 将 main.py 的逻辑封装为 HTTP POST 接口"""

from fastapi import APIRouter
from core.agent import agent
from api.models.requests import ChatRequest
from api.models.responses import ApiResponse

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/", response_model=ApiResponse)
def chat(req: ChatRequest):
    """
    聊天接口：接收用户消息，调用 LangChain Agent 返回回答
    请求体: {"content": "北京今天多少度？穿什么衣服？"}
    """
    response = agent.invoke({
        "messages": [
            {"role": "user", "content": req.content}
        ]
    })

    # 从 response 中提取最终回答
    answer = response.get("output", str(response))
    

    return ApiResponse(data=answer)
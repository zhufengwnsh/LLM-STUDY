"""通用智能助手路由

路由层仅做两件事：
1. 将用户请求转发给 LangGraph Agent（MCPAgent）
2. 管理多步骤会话（checkpoint）

不含任何业务逻辑、关键词判断或硬编码协议。
所有语义决策（需要调用哪个工具、需要什么参数、是否需要多步骤交互）
都由 LLM 通过 LangGraph 自主决定。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from api.models.responses import ApiResponse
from api.checkpoint import checkpoint_store
from core.agent_clothing_advise import MCPAgent
from langchain_core.load import dumps, loads

router = APIRouter(prefix="/api/clothing_advise", tags=["ClothingAdvise"])


class AdviseRequest(BaseModel):
    """请求体"""
    content: str
    session_id: Optional[str] = None


class LocationRequest(BaseModel):
    """补充信息的请求体

    content 可以是任意自然语言，例如：
    - "我在北京"
    - "116.4,39.9"
    - "上海市浦东新区"
    LLM 会自主理解并决定如何调用工具。
    """
    session_id: str
    content: str


# 全局单例 Agent（延迟加载 MCP 工具）
_agent = MCPAgent()


@router.post("/advise", response_model=ApiResponse)
def advise(req: AdviseRequest):
    """
    通用智能助手接口

    所有决策由 LLM 自主完成，路由层不做任何业务假设。
    通过 session_id 支持多步骤会话，session 中保存完整消息历史。

    请求体:
    - content: 用户输入
    - session_id: 可选，首次不传
    """
    if not req.session_id:
        # ========== 新会话 ==========
        text, messages = _agent.get_full_messages(content=req.content)

        # 序列化完整消息历史并存入 session
        session_id = checkpoint_store.create_session()
        checkpoint_store.update_session(session_id, {
            "messages": dumps(messages),
        })
        checkpoint_store.set_step(session_id, "active")

        return ApiResponse(data={
            "session_id": session_id,
            "message": text,
        })

    # ========== 已有会话 ==========
    session = checkpoint_store.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=400, detail="session_id 无效或已过期")

    # 从 session 恢复历史消息
    history_messages = loads(session["context"].get("messages", "[]"))

    # 新输入追加到历史后交给 LLM
    text, messages = _agent.get_full_messages_with_history(
        content=req.content,
        history_messages=history_messages,
    )

    # 更新会话中的消息历史
    checkpoint_store.update_session(req.session_id, {
        "messages": dumps(messages),
    })

    return ApiResponse(data={
        "session_id": req.session_id,
        "message": text,
    })


@router.post("/location", response_model=ApiResponse)
def update_location(req: LocationRequest):
    """
    用户补充信息的接口

    LLM 如果发现自己缺少必要信息（如地理位置），会通过之前的回复引导用户提供。
    用户提供信息后，前端调用此接口将信息传入，LLM 结合完整会话历史继续处理。

    请求体:
    - session_id: 会话 ID
    - content: 用户的补充信息（自然语言），例如 "我在北京"、"116.4,39.9"
    """
    session = checkpoint_store.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=400, detail="session_id 无效或已过期")

    # 从 session 恢复完整历史消息
    history_messages = loads(session["context"].get("messages", "[]"))

    # 将用户的新输入追加到历史末尾，LLM 感知完整上下文后继续处理
    text, messages = _agent.get_full_messages_with_history(
        content=req.content,
        history_messages=history_messages,
    )

    # 更新会话中的消息历史（不删除 session，对话可以继续）
    checkpoint_store.update_session(req.session_id, {
        "messages": dumps(messages),
    })

    return ApiResponse(data={
        "session_id": req.session_id,
        "message": text,
    })
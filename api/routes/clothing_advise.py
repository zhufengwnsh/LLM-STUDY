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

router = APIRouter(prefix="/api/clothing_advise", tags=["ClothingAdvise"])


class AdviseRequest(BaseModel):
    """请求体"""
    content: str
    session_id: Optional[str] = None


class LocationRequest(BaseModel):
    """经纬度请求体"""
    session_id: str
    lng: float
    lat: float


# 全局单例 Agent（延迟加载 MCP 工具）
_agent = MCPAgent()


@router.post("/advise", response_model=ApiResponse)
def advise(req: AdviseRequest):
    """
    通用智能助手接口

    所有决策由 LLM 自主完成，路由层不做任何业务假设。
    仅通过 session_id 支持多步骤会话：
    - 无 session_id → 新会话，交给 LLM 处理
    - 有 session_id → 恢复上下文，结合新输入交给 LLM

    请求体:
    - content: 用户输入
    - session_id: 可选，首次不传
    """
    if not req.session_id:
        # 新会话，直接交给 LLM
        result = _agent.run(content=req.content)

        # 创建 session 保存上下文，支持后续继续交互
        session_id = checkpoint_store.create_session({
            "original_content": req.content,
        })
        checkpoint_store.update_session(session_id, {
            "last_response": result,
        })
        checkpoint_store.set_step(session_id, "active")

        return ApiResponse(data={
            "session_id": session_id,
            "message": result,
        })

    # 已有会话
    session = checkpoint_store.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=400, detail="session_id 无效或已过期")

    # 交给 LLM（带上新输入）
    result = _agent.run(content=req.content)

    # 更新上下文
    checkpoint_store.update_session(req.session_id, {
        "last_response": result,
    })

    return ApiResponse(data={
        "session_id": req.session_id,
        "message": result,
    })


@router.post("/location", response_model=ApiResponse)
def update_location(req: LocationRequest):
    """
    提供额外参数后的处理接口

    请求体:
    - session_id: 会话 ID
    - lng: 经度
    - lat: 纬度
    """
    session = checkpoint_store.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=400, detail="session_id 无效或已过期")

    original_content = session.get("context", {}).get("original_content", "")

    # 将额外参数传给 Agent，LLM 自主决定如何使用
    result = _agent.run(
        content=original_content,
        lng=req.lng,
        lat=req.lat,
    )

    checkpoint_store.delete_session(req.session_id)

    return ApiResponse(data={
        "message": result,
    })
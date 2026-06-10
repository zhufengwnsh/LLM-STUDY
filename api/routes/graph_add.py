"""四则表达式计算 - 使用 LangGraph Agent 自动解析并计算结果"""

from fastapi import APIRouter, Query
from api.models.responses import ApiResponse
from graph.add_multi import run_agent

router = APIRouter(prefix="/api/graph", tags=["Calculator"])


@router.get("/add", response_model=ApiResponse)
def graph_add(content: str = Query(..., description="输入四则表达式，例如: Add 3 and 4*5")):
    """
    使用 LangGraph Agent 自动解析四则表达式并返回计算结果
    """
    try:
        data = run_agent(content)

        print(f"调用graph_add计算api, 表达式: {content}, 结果: {data}")
        return ApiResponse(data=data)
    except Exception as e:
        error_msg = f"计算失败: {str(e)}"
        print(error_msg)
        return ApiResponse(code=1, message="error", data=error_msg)
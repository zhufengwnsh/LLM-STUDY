from pydantic import BaseModel
from typing import Any, Optional


class ApiResponse(BaseModel):
    """统一 API 响应格式"""
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None
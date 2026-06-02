from pydantic import BaseModel


class ChatRequest(BaseModel):
    """聊天请求体"""
    content: str


class ClothingRequest(BaseModel):
    """穿衣建议请求体"""
    temperature: float


class WeatherRequest(BaseModel):
    """天气查询请求体"""
    city: str
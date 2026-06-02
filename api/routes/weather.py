"""天气查询相关路由"""

from fastapi import APIRouter, Query
from api.models.responses import ApiResponse

router = APIRouter(prefix="/api/weather", tags=["Weather"])


@router.get("/", response_model=ApiResponse)
def get_weather(city: str = Query(..., description="城市名称")):
    """
    查询指定城市的温度,入参为城市名称
    """
    data="北京 当前的温度：22摄氏度";
    if(city.startswith("北京")):
        data="北京 当前的温度：22摄氏度"
    elif(city.startswith("上海")):
        data="上海 当前的温度：32摄氏度"
    else:
        data="哈尔滨 当前的温度：12摄氏度"
    # 模拟真实接口返回数据
    return ApiResponse(data=data)
"""根据经纬度查询城市名称"""

from fastapi import APIRouter, Query
from api.models.responses import ApiResponse

router = APIRouter(prefix="/api/city", tags=["city"])


@router.get("/", response_model=ApiResponse)
def get_weather(lng: float = Query(..., description="经度"),lat: float = Query(..., description="纬度")):
    """
    根据经纬度查询城市名称
    """
    data="武汉";
    if(lng>=300 and lat >=300):
        data="北京"
    elif(lng>=200 and lat >=200):
        data="上海"
    elif(lng>=100 and lat >=100):
        data="哈尔滨"
    else:
        data="武汉"
    # 模拟真实接口返回数据
    print(f"调用城市查询api,返回结果:{data}")
    return ApiResponse(data=data)
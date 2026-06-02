"""穿衣建议相关路由"""

from fastapi import APIRouter
from api.models.requests import ClothingRequest
from api.models.responses import ApiResponse

router = APIRouter(prefix="/api/clothing", tags=["Clothing"])


@router.post("/note", response_model=ApiResponse)
def clothing_note(req: ClothingRequest):
    """
    根据温度给出穿衣建议
    请求体: {"temperature": 25}
    """
    temp = req.temperature
    if temp < 20:
        result = f"今天温度{temp}度,偏冷多穿衣服"
    elif temp < 30:
        result = f"今天温度{temp}度,温度适宜建议穿薄外套"
    else:
        result = f"今天温度{temp}度,偏热可以穿短袖"
    print(f"调用穿衣建议api,返回结果:{result}")
    return ApiResponse(data=result)
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# 定义请求体模型
class ClothingReq(BaseModel):
    temperature: float
    
# 接口1：给 Skill1 调用 → 返回温度
@app.get("/weather")
def get_weather(city: str):
    print("收到温度查询请求")
    # 模拟真实接口返回数据
    return {"code": 0, "data": f"{city} 当前的温度：22摄氏度"}

# 接口2：给 Skill2 调用 → 返回穿衣建议
@app.post("/clothing-note")
def clothing_note(req: ClothingReq):
    print("收到穿衣建议请求，温度：", req.temperature)
    result=''
    if req.temperature < 20 :
        result = f"今天温度{req.temperature}度,偏冷多穿衣服"
    elif req.temperature < 30 :
        result = f"今天温度{req.temperature}度,温度适宜建议穿薄外套 "
    else:
        result = f"今天温度{req.temperature}度,偏热可以穿短袖"
    return {
        "code": 0,
        "data": result
    }
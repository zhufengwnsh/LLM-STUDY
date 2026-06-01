from langchain.tools import tool
import requests

@tool
def get_current_temperature(city: str) -> str:
    """
    根据城市名获取当前温度，必须先调用这个工具获取温度数据
    参数：city 城市名称
    """
    try:
        # 调用本地接口 1
        resp = requests.get("http://127.0.0.1:8000/weather", params={"city": city}, timeout=10)
        return resp.json()["data"]
    except:
        return "获取温度失败"
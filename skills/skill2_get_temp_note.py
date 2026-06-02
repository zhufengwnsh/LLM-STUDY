from langchain.tools import tool
import requests

@tool
def generate_clothing_note(temp: float) -> str:
    """
    根据温度生成穿衣建议，必须在获取温度后调用这个工具
    参数：temp 温度字符串，例如 25℃
    """
    try:
        # 调用本地接口 2
        resp = requests.post(
            "http://127.0.0.1:8080/api/clothing/note",
            json={"temperature": temp},
            timeout=10
        )
        return resp.json()["data"]
    except Exception as e:
        print(f"【报错】: {e}")
        return "生成穿衣建议失败"
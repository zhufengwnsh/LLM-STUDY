from core.agent import agent
import os
from config.settings import LLM_API_KEY

print(f"env:{os.getenv('ENV','not-set')}")
print(f"setting_key:{LLM_API_KEY}")
print(f"load_key:{os.getenv('LLM_API_KEY')}")

# 1.x 格式必须是 messages 格式
# response = agent.invoke({
#     "messages": [
#         {"role": "user", "content": "北京今天多少度？穿什么衣服？"}
#     ]
# })

# # 输出最终回答
# print("\n【回答】：")
# print(response)

# import os ,sys,    datetime load_dotenv   openai    
# utf8, load env, client, response
# print content + datetime, token usage
# assert finish_reason,   content.len > 0,  completion_tokens > 0
import os
import sys
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI

if hasattr(sys.stdout,"reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8",errors="replace")

load_dotenv()
client = OpenAI(api_key=os.environ["LLM_API_KEY"],base_url=os.environ["LLM_BASE_URL"])
response = client.chat.completions.create(model="deepseek-chat",max_tokens=100,messages=[{"role":"user","content":"用一句话介绍自己"}])  

print(f"deepseek响应:{response.choices[0].message.content}")
print(f"deepseek token使用情况:{response.usage}, 总的token使用数量:{response.usage.total_tokens}")

assert response.choices[0].finish_reason in ('stop','finish'), f"出现异常:{response.choices[0].finish_reason}"
assert len(response.choices[0].message.content) > 0, "响应不能为空"
assert response.usage.completion_tokens > 0, "token不能为空"

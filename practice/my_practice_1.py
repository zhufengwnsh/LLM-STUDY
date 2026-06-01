import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

if hasattr(sys.stdout,"reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8",errors="replace")

load_dotenv()
client = OpenAI(api_key=os.environ["LLM_API_KEY"],base_url=os.environ["LLM_BASE_URL"])
response = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=100,
    messages=[{"role":"user","content":"用一句话自我介绍"}]
)
print("deepseek响应:",response)
print("deepseek响应:",response.choices[0].message.content,datetime.now().strftime("%Y%m%d%H%M%S"))
print(f"token使用情况: prompt->{response.usage.prompt_tokens},compeletion->{response.usage.completion_tokens},total->{response.usage.total_tokens}")

assert response.choices[0].finish_reason in ('stop','finish'), f"出现异常,异常原因:{response.choices[0].finish_reason}"
assert len(response.choices[0].message.content) > 0, "响应不能为空"
assert response.usage.completion_tokens > 0, ""
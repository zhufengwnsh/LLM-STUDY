import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["LLM_API_KEY"],
    base_url=os.environ["LLM_BASE_URL"],
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "用一句话自我介绍"},
    ],
)

print("DeepSeek 响应:",response)
print(response.choices[0].message.content)
print()
print("Token 使用情况:")
print(f"  prompt_tokens:     {response.usage.prompt_tokens}")
print(f"  completion_tokens: {response.usage.completion_tokens}")
print(f"  total_tokens:      {response.usage.total_tokens}")

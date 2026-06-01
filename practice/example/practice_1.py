import os
import json
import urllib.request

from dotenv import load_dotenv

load_dotenv()

api_key = os.environ["LLM_API_KEY"]
base_url = os.environ["LLM_BASE_URL"]
url = f"{base_url}/chat/completions"

payload = json.dumps({
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": "用一句话自我介绍"},
    ],
}).encode("utf-8")

req = urllib.request.Request(
    url,
    data=payload,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    },
)

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))

print("DeepSeek 响应:")
print(data["choices"][0]["message"]["content"])
print()
print("Token 使用情况:")
print(f"  prompt_tokens:     {data['usage']['prompt_tokens']}")
print(f"  completion_tokens: {data['usage']['completion_tokens']}")
print(f"  total_tokens:      {data['usage']['total_tokens']}")

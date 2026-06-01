import os
import sys
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI

if hasattr(sys.stdout,"reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8",errors="replace")
load_dotenv()    
client = OpenAI(api_key=os.environ.get("LLM_API_KEY"),base_url=os.environ["LLM_BASE_URL"])

PROMPTS = {
    "中文":"用一句话描述一只猫在做什么",
    "ENGLISH":"Describe in one sentence what a cat is doing."
}
N=10
for label, prompt in PROMPTS.items():
    OUT_TOKENS = []
    OUT_CONTENTS = []
    for _ in range(5):
        response = client.chat.completions.create(model="deepseek-chat",max_tokens=100,temperature=1.2,
                                                  messages=[{"role":"user","content":prompt}])
        OUT_TOKENS.append(response.usage.completion_tokens)
        OUT_CONTENTS.append(response.choices[0].message.content)
    print(f"prompt:{prompt}, input cost:{response.usage.prompt_tokens}")
    print(f"prompt:{prompt}, output cost:{OUT_TOKENS} max:{max(OUT_TOKENS)}, min:{min(OUT_TOKENS)}")
    print(f"return:{OUT_CONTENTS}")
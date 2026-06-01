from langchain_openai import ChatOpenAI
from config.settings import LLM_BASE_URL, LLM_MODEL, LLM_API_KEY

# 对接 DeepSeek，兼容 OpenAI 协议
def get_llm():
    return ChatOpenAI(
        model=LLM_MODEL,
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL,
        temperature=0.1
    )
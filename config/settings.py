import os
from dotenv import load_dotenv

# 第1步：加载 .env 文件，获取 ENV 配置（默认 qa）
load_dotenv(".env")
env_name = os.getenv("ENV", "qa")

# 第2步：根据 ENV 加载对应的环境配置文件
env_file = f".env.{env_name}"
if os.path.exists(env_file):
    load_dotenv(env_file, override=True)


# 第4步：环境变量中的值优先（来自 .env.{env_name} 文件）
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL")
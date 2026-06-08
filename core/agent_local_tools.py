from langchain.agents import create_agent  # 1.x 唯一官方函数
from langchain.tools import tool
from core.llm import get_llm

import config  # 初始化配置：读取 .env → 获取 ENV → 加载对应 .env.{ENV}

# 1.x 用 ChatOpenAI 兼容 DeepSeek
llm = get_llm()

# ==================== 从你的 skills 目录导入工具 ====================
from skills.skill1_get_weather import get_current_temperature
from skills.skill2_get_temp_note import generate_clothing_note

# 注册到 tools 列表
tools = [get_current_temperature, generate_clothing_note]

# ==================== LangChain 1.x 标准写法 ====================
# 没有 create_tool_calling_agent
# 没有 AgentExecutor
# 没有 prompt 参数
# 这是 1.x 唯一正确写法！

skillAgent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
    1. 你必须严格调用工具回答问题，不能自己编造答案。
    2. 工具如果有返回结果, 直接展示工具的返回结果不要自己加任何东西
    3. 工具如果没有返回或者返回了报错信息,直接提示用户错误信息
    4. 返回数据严格按如下格式,直接将skill返回的数字填入xxx: 今天天气xxx度,穿衣建议:xxx
    """
)
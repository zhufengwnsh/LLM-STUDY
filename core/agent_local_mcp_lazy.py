import asyncio

from langchain.agents import create_agent  # 1.x 唯一官方函数
from langchain_mcp_adapters.client import MultiServerMCPClient
from core.llm import get_llm

import config  # 初始化配置：读取 .env → 获取 ENV → 加载对应 .env.{ENV}

# 1.x 用 ChatOpenAI 兼容 DeepSeek
llm = get_llm()

# ==================== 通过 MCP SERVER 加载工具 ====================
# MCP 服务器地址: localhost:8080/mcp
mcp_client = MultiServerMCPClient({
    "local": {
        "url": "http://localhost:8080/mcp",
        "transport": "http",
    }
})


def _make_sync_tool(tool):
    """给异步 StructuredTool 裹一层 sync func，兼容 LangChain 1.x 同步调用。

    langchain-mcp-adapters 返回的 StructuredTool 只设置了 coroutine（异步），
    没有设置 func（同步），但 LangChain 1.x create_agent 用的是同步调用，
    直接调用会报错: NotImplementedError: StructuredTool does not support sync invocation.
    """
    if tool.coroutine is None:
        return tool

    async_fn = tool.coroutine

    def sync_fn(**kwargs):
        return asyncio.run(async_fn(**kwargs))

    # 复用原 StructuredTool 的全部元数据，补上 sync func
    from langchain_core.tools import StructuredTool
    return StructuredTool(
        name=tool.name,
        description=tool.description,
        args_schema=tool.args_schema,
        func=sync_fn,
        coroutine=async_fn,
        response_format=tool.response_format,
        metadata=tool.metadata,
    )


class LazyAgent:
    """代理对象：第一次调用 .invoke() 时才连接 MCP 获取工具并创建 Agent。

    解决启动时序问题：
    - core/agent.py 在模块导入时就会加载
    - 但 MCP server 要在 uvicorn 启动后才可用
    - 所以推迟到实际调用时再连接 MCP
    """

    def __init__(self):
        self._agent = None

    def _ensure(self):
        if self._agent is not None:
            return self._agent

        async def _init():
            raw_tools = await mcp_client.get_tools()
            # 给每个工具裹上 sync 兼容层
            tools = [_make_sync_tool(t) for t in raw_tools]
            return create_agent(
                model=llm,
                tools=tools,
                system_prompt="""
                1. 你必须严格调用工具回答问题，不能自己编造答案。
                2. 工具如果有返回结果, 直接展示工具的返回结果不要自己加任何东西
                3. 工具如果没有返回或者返回了报错信息,直接提示用户错误信息
                4. 返回数据严格按如下格式,直接将skill返回的数字填入xxx: 今天天气xxx度,穿衣建议:xxx
                """
            )

        self._agent = asyncio.run(_init())
        return self._agent

    def invoke(self, *args, **kwargs):
        return self._ensure().invoke(*args, **kwargs)


lazyMcpAgent = LazyAgent()
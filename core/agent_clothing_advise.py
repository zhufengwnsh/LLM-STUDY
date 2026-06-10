"""基于 LangGraph + MCP 的通用智能 Agent

纯 LangGraph 实现：
- LLM 通过 tool_calls 自主决策调用 MCP 工具还是直接返回文本
- _should_continue 根据 tool_calls 判断是否继续循环
- 不含任何业务逻辑、硬编码协议或关键词判断
"""

import asyncio
import operator

from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from typing_extensions import TypedDict, Annotated
from typing import Literal, Optional
from langgraph.graph import StateGraph, START, END
from core.llm import get_llm

import config

# ==================== MCP 服务器连接配置 ====================
mcp_client = MultiServerMCPClient({
    "local": {
        "url": "http://localhost:8080/mcp",
        "transport": "http",
    }
})


def _make_sync_tool(tool):
    """给异步 StructuredTool 裹一层 sync func，兼容 LangChain 1.x 同步调用。"""
    if tool.coroutine is None:
        return tool

    async_fn = tool.coroutine

    def sync_fn(**kwargs):
        return asyncio.run(async_fn(**kwargs))

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


# ==================== Agent State ====================


class AgentState(TypedDict):
    """Graph 状态：仅包含消息列表"""
    messages: Annotated[list[AnyMessage], operator.add]


# ==================== LangGraph Agent ====================


class MCPAgent:
    """基于 LangGraph + MCP 的通用智能 Agent

    纯 LangGraph 实现，不含任何业务逻辑：
    - LLM 通过 tool_calls 自主决策调用 MCP 工具还是直接回答
    - _should_continue 根据 tool_calls 判断是否继续循环
    """

    def __init__(self):
        self._model = get_llm()
        self._tools = None
        self._tools_by_name = {}
        self._model_with_tools = None
        self._agent = None

    def _ensure_tools(self):
        """延迟加载 MCP 工具（只在首次调用时连接 MCP 服务器）"""
        if self._tools is not None:
            return

        async def _fetch():
            raw_tools = await mcp_client.get_tools()
            return [_make_sync_tool(t) for t in raw_tools]

        self._tools = asyncio.run(_fetch())
        self._tools_by_name = {t.name: t for t in self._tools}
        self._model_with_tools = self._model.bind_tools(self._tools)

    # ------------------------------------------------------------------
    # Graph node callbacks
    # ------------------------------------------------------------------

    def _llm_call(self, state: AgentState):
        """LLM 决定是调用 MCP 工具还是直接回答"""
        self._ensure_tools()
        return {
            "messages": [
                self._model_with_tools.invoke([
                    SystemMessage(content="""你是一个智能助手。你可以通过 MCP 工具获取外部数据来完成用户请求。
                    可用的 MCP 工具会由系统自动加载，你需要根据用户输入判断：
                    1. 如果可以使用工具获取所需信息 → 调用对应工具, 如果用户的问题只是闲聊跟工具无关,可直接返回LLM的回答
                    2. 如果信息不足无法调用工具 → 直接告诉用户需要提供什么信息
                    3. 拿到工具返回结果后，根据需要决定下一步（继续调用其他工具或直接回答）
                    4. 所有信息齐全后，如果流程结束并且工具给了最终返回结果,直接返回工具返回的信息不要自己加工
                    注意：
                    - 每次只能调用一个工具
                    - 拿到工具返回结果后，分析结果再决定下一步"""),
                    *state["messages"]
                ])
            ]
        }

    def _tool_node(self, state: AgentState):
        """执行 MCP 工具调用"""
        result = []
        for tool_call in state["messages"][-1].tool_calls:
            tool = self._tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
        return {"messages": result}

    @staticmethod
    def _should_continue(state: AgentState) -> Literal["tool_node", "__end__"]:
        """判断是否继续循环：
        - LLM 请求调用工具 → 进入 tool_node
        - 否则 → 结束
        """
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tool_node"
        return END

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------

    def _build_agent(self):
        """构建 LangGraph：LLM 自主决策调用 MCP 还是结束"""
        builder = StateGraph(AgentState)

        builder.add_node("llm_call", self._llm_call)
        builder.add_node("tool_node", self._tool_node)

        builder.add_edge(START, "llm_call")
        builder.add_conditional_edges(
            "llm_call",
            self._should_continue,
            ["tool_node", END]
        )
        builder.add_edge("tool_node", "llm_call")

        return builder.compile()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, content: str) -> str:
        """执行智能助手流程

        Args:
            content: 用户输入
            
        Returns:
            LLM 的原始返回文本
        """
        self._ensure_tools()

        if self._agent is None:
            self._agent = self._build_agent()


        initial_state = {
            "messages": [HumanMessage(content=content)],
        }

        result = self._agent.invoke(initial_state)
        final_message = result["messages"][-1]
        return final_message.content


# 默认单例
default_agent = MCPAgent()
run_agent = default_agent.run
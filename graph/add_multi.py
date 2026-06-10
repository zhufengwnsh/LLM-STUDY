"""四则表达式计算 Agent - 使用 LangGraph Agent 自动解析并计算结果"""

from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from typing_extensions import TypedDict, Annotated
from typing import Literal
from langgraph.graph import StateGraph, START, END
from config.settings import LLM_BASE_URL, LLM_MODEL, LLM_API_KEY
import operator


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int


class ArithmeticAgent:
    """基于 LangGraph 的四则表达式计算 Agent

    封装 LLM + Tool 的完整调用流程，每个实例拥有独立的模型和计算图，
    可安全用于并发场景。

    用法:
        agent = ArithmeticAgent()
        result = agent.run("Add 3 and 4*5")
    """

    def __init__(self):
        self._model = init_chat_model(
            LLM_MODEL,
            model_provider="openai",
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL,
            temperature=0
        )
        self._tools = self._define_tools()
        self._tools_by_name = {t.name: t for t in self._tools}
        self._model_with_tools = self._model.bind_tools(self._tools)
        self._agent = self._build_agent()

    # ------------------------------------------------------------------
    # Tool definitions
    # ------------------------------------------------------------------

    @staticmethod
    def _define_tools():
        @tool
        def multiply(a: int, b: int) -> int:
            """Multiply `a` and `b`.

            Args:
                a: First int
                b: Second int
            """
            return a * b

        @tool
        def add(a: int, b: int) -> int:
            """Adds `a` and `b`.

            Args:
                a: First int
                b: Second int
            """
            return a + b

        @tool
        def divide(a: int, b: int) -> float:
            """Divide `a` and `b`.

            Args:
                a: First int
                b: Second int
            """
            return a / b

        return [add, multiply, divide]

    # ------------------------------------------------------------------
    # Graph node callbacks
    # ------------------------------------------------------------------

    def _llm_call(self, state: dict):
        """LLM decides whether to call a tool or not"""

        return {
            "messages": [
                self._model_with_tools.invoke(
                    [
                        SystemMessage(
                            content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
                        )
                    ]
                    + state["messages"]
                )
            ],
            "llm_calls": state.get('llm_calls', 0) + 1
        }

    def _tool_node(self, state: dict):
        """Performs the tool call"""

        result = []
        for tool_call in state["messages"][-1].tool_calls:
            tool = self._tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
        return {"messages": result}

    @staticmethod
    def _should_continue(state: MessagesState) -> Literal["tool_node", "__end__"]:
        """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

        messages = state["messages"]
        last_message = messages[-1]

        if last_message.tool_calls:
            return "tool_node"
        return END

    # ------------------------------------------------------------------
    # Agent graph construction
    # ------------------------------------------------------------------

    def _build_agent(self):
        builder = StateGraph(MessagesState)

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
        """执行四则表达式计算

        Args:
            content: 四则表达式文本，例如 "Add 3 and 4*5"

        Returns:
            计算结果的字符串

        Raises:
            Exception: 计算过程抛出的异常
        """
        messages = [HumanMessage(content=content)]
        result = self._agent.invoke({"messages": messages})
        final_message = result["messages"][-1]
        return final_message.content


# 默认单例实例，方便快速导入使用
default_agent = ArithmeticAgent()
run_agent = default_agent.run
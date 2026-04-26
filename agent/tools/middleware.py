r"""middleware
@Time: 2026-04-27 04:28
@File: agent\tools\middleware.py
@Description: middleware
"""

from collections.abc import Callable
from typing import Any, cast

from langchain.agents import AgentState
from langchain.agents.middleware import (
    ModelRequest,
    before_model,
    dynamic_prompt,
    wrap_tool_call,
)
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command

from utils.logger_handler import logger
from utils.prompt_loader import load_report_prompts, load_system_prompts


@wrap_tool_call
def monitor_tool(
    # 请求前的数据封装
    request: ToolCallRequest,
    # 执行的函数本身
    handler: Callable[[ToolCallRequest], ToolMessage | Command[Any]],
) -> ToolMessage | Command[Any]:
    """
    工具执行的监控
    :param request: 工具执行的请求
    :param handler: 工具执行的函数
    :return: 工具执行的结果
    """

    logger.info(f"[Tool monitor] 执行工具: {request.tool_call['name']}")
    logger.info(f"[Tool monitor] 工具参数: {request.tool_call['args']}")

    try:
        result = handler(request)
        logger.info(f"[Tool monitor] 工具{request.tool_call['name']}调用成功")

        if request.tool_call["name"] == "fill_context_for_report":
            ctx = request.runtime.context
            if ctx is not None:
                # 提示词切换标记
                ctx["report"] = True

        return result
    except Exception as e:
        logger.error(f"[Tool monitor] 工具{request.tool_call['name']}调用失败: {e}")
        raise e


@before_model
def log_before_model(
    state: AgentState,
    runtime: Runtime,
) -> None:  # before_model：每一轮调用模型前各触发一次（含 ReAct 多轮）
    """
    每次调用模型前输出日志（ReAct 中每一轮推理前都会触发）
    :param state: 整个 Agent 智能体中的状态记录
    :param runtime: 整个执行过程的上下文
    :return: None
    """
    logger.info(f"[Log before model] 即将调用模型，带有{len(state['messages'])}条消息")

    # 末尾消息即当前轮上下文最后一条；其content在LangChain中常为 str也可能是多模态块list
    last = state["messages"][-1]
    raw = last.content
    text = raw.strip() if isinstance(raw, str) else str(raw)  # 日志单行化
    logger.debug(f"[Log before model] {type(last).__name__} | {text}")

    return None


@dynamic_prompt  # 每一次在生成提示词前，调用该函数
def report_prompt_switch(request: ModelRequest) -> str:  # 动态切换提示词
    ctx = cast(dict[str, Any], request.runtime.context or {})
    is_report = bool(ctx.get("report", False))
    print("*" * 50)
    if is_report:  # 报告生成场景
        print("*" * 50)
        print("报告生成场景")
        return load_report_prompts()

    return load_system_prompts()

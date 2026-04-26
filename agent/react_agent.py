r"""react_agent
@Time: 2026-04-27 05:08
@File: agent\react_agent.py
@Description: react_agent
"""

from collections.abc import Iterator

from langchain.agents import create_agent

from agent.tools.agent_tools import (
    fetch_external_data,
    fill_context_for_report,
    get_current_month,
    get_user_id,
    get_user_location,
    get_weather,
    rag_summarize,
)
from agent.tools.middleware import log_before_model, monitor_tool, report_prompt_switch
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts


class ReactAgent:
    def __init__(self) -> None:
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=[
                rag_summarize,
                get_weather,
                get_user_location,
                get_user_id,
                get_current_month,
                fetch_external_data,
                fill_context_for_report,
            ],
            middleware=[
                monitor_tool,
                log_before_model,
                report_prompt_switch,
            ],
        )

    def execute_stream(self, query: str) -> Iterator[str]:
        input_dist = {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        }

        # 第三个参数context是上下文runtime中的信息，提示词切换标记
        for chunk in self.agent.stream(  # type: ignore[call-overload]
            input_dist, stream_mode="values", context={"report": False}
        ):
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                yield latest_message.content.strip() + "\n"


if __name__ == "__main__":
    agent = ReactAgent()

    for chunk in agent.execute_stream("扫地机器人在我所在的地区的气温下如何保养"):
        print(chunk, end="", flush=True)

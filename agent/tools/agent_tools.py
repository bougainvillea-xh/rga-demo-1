r"""agent_tools
@Time: 2026-04-27 02:47
@File: agent\tools\agent_tools.py
@Description: agent_tools
"""

import json
import os
import random

from langchain_core.tools import tool

from rag.rag_service import RagSummarizeService
from utils.config_handler import agent_config
from utils.logger_handler import logger
from utils.path_tool import get_abs_path

rag = RagSummarizeService()
user_ids = [
    "1001",
    "1002",
    "1003",
    "1004",
    "1005",
    "1006",
    "1007",
    "1008",
    "1009",
    "1010",
]
month_arr = [
    "2025-01",
    "2025-02",
    "2025-03",
    "2025-04",
    "2025-05",
    "2025-06",
    "2025-07",
    "2025-08",
    "2025-09",
    "2025-10",
    "2025-11",
    "2025-12",
]
external_data: dict[str, dict[str, dict[str, str]]] = {}


@tool(description="从向量存储种检索参考资料")
def rag_summarize(query: str) -> str:
    return rag.rag_summarize(query)


@tool(description="获取指定城市天气，以字符串形式返回")
def get_weather(city: str) -> str:
    return f"城市{city}天气为晴天，气温26摄氏度，空气湿度50%，南风1级，AQI21,最近6小时降雨概率极低"  # noqa: E501


@tool(description="获取用户当前城市，以字符串形式返回")
def get_user_location() -> str:
    return random.choice(["北京", "上海", "广州", "深圳", "成都", "重庆"])


@tool(description="获取用户ID，以字符串形式返回")
def get_user_id() -> str:
    return random.choice(user_ids)


@tool(description="获取当前月份，以字符串形式返回")
def get_current_month() -> str:
    return random.choice(month_arr)


def generate_external_data() -> None:
    """
    {
        "user_id": {
            "month": {"特征": "xxx", "效率": "xxx", ...},
            "month": {"特征": "xxx", "效率": "xxx", ...},
            ...
        },
        "user_id": {
            "month": {"特征": "xxx", "效率": "xxx", ...},
            "month": {"特征": "xxx", "效率": "xxx", ...},
            ...
        },
        ...
    }
    :return:
    """
    if not external_data:
        external_data_path = get_abs_path(agent_config["external_data_path"])
        print(external_data_path)
        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"外部数据文件不存在: {external_data_path}")
        with open(external_data_path, encoding="utf-8") as f:
            for line in f.readlines()[1:]:
                arr: list[str] = line.strip().split(",")

                user_id = arr[0].replace('"', "")
                feature = arr[1].replace('"', "")
                efficiency = arr[2].replace('"', "")
                consumables = arr[3].replace('"', "")
                comparison = arr[4].replace('"', "")
                time = arr[5].replace('"', "")

                if user_id not in external_data:
                    external_data[user_id] = {}

                external_data[user_id][time] = {
                    "特征": feature,
                    "效率": efficiency,
                    "耗材": consumables,
                    "对比": comparison,
                }


def _fetch_external_data(user_id: str, month: str) -> str:
    generate_external_data()
    try:
        return json.dumps(external_data[user_id][month], ensure_ascii=False)
    except KeyError:
        logger.warning(
            f"[fetch_external_data] 未能检索到用户: {user_id}在{month}的使用记录"
        )
        return ""


@tool(
    description="从外部系统获取指定用户、指定月份的使用记录（特征/效率/耗材/对比）；无记录时返回空字典"
)
def fetch_external_data(user_id: str, month: str) -> str:
    return _fetch_external_data(user_id, month)


@tool(
    description="无入参，无返回值，调用后触发中间件自动为报告生成的场景动态注入上下文信息，为后续提示词切换提供上下文信息"
)
def fill_context_for_report() -> str:
    return "fill_context_for_report 已调用"


if __name__ == "__main__":
    print(_fetch_external_data("1021", "2025-01"))

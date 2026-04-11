r"""config_handler
@Time: 2026-03-27 15:17
@File: utils\config_handler.py
"""

from typing import Any, cast

import yaml
from dotenv import load_dotenv

from utils.path_tool import get_abs_path

load_dotenv(get_abs_path(".env"))


def _load_config(config_file: str, encoding: str = "utf-8") -> dict[str, Any]:
    """
    加载配置文件
    :param config_file: 配置文件路径
    :param encoding: 编码
    :return: 配置字典
    """
    file_path = get_abs_path(config_file)
    with open(file_path, encoding=encoding) as f:
        return cast(dict[str, Any], yaml.safe_load(f))


def load_rag_config() -> dict[str, Any]:
    return _load_config("config/rag.yaml")


def load_chroma_config() -> dict[str, Any]:
    return _load_config("config/chroma.yaml")


def load_prompts_config() -> dict[str, Any]:
    return _load_config("config/prompts.yaml")


def load_agent_config() -> dict[str, Any]:
    return _load_config("config/agent.yaml")


rag_config = load_rag_config()
chroma_config = load_chroma_config()
prompts_config = load_prompts_config()
agent_config = load_agent_config()


if __name__ == "__main__":
    print(prompts_config["system_prompt_path"])

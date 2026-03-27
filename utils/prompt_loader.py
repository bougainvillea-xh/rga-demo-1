r"""prompt_loader
@Time: 2026-03-27 16:55
@File: utils\prompt_loader.py
"""

from utils.config_handler import prompts_config
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


def _load_prompt_file(config_key: str, log_prefix: str) -> str:
    """
    通用提示词加载函数
    :param config_key: 配置文件中的键名，例如 'system_prompt_path'
    :param log_prefix: 日志中用于标识的前缀，例如 'load_system_prompts'
    """
    try:
        # 获取路径
        raw_path = prompts_config[config_key]
        abs_path = get_abs_path(raw_path)
    except KeyError:
        logger.error(f"[{log_prefix}] 配置文件中缺少必要配置项：{config_key}")
        raise  # 使用裸 raise 保留原始堆栈信息

    try:
        # 2. 资源管理优化：使用 with 确保文件关闭
        with open(abs_path, encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"[{log_prefix}] 解析文件失败 ({abs_path}): {e}")
        raise


def load_system_prompts() -> str:
    return _load_prompt_file("system_prompt_path", "load_system_prompts")


def load_rag_prompts() -> str:
    return _load_prompt_file("rag_summarize_prompt_path", "load_rag_prompts")


def load_report_prompts() -> str:
    return _load_prompt_file("report_prompt_path", "load_report_prompts")


if __name__ == "__main__":
    print(load_system_prompts())
    print(load_rag_prompts())
    print(load_report_prompts())

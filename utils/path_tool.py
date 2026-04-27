r"""path_tool
@Time: 2026-03-27 14:46
@File: utils\path_tool.py
"""

import os


def get_project_root() -> str:
    """
    获取项目根目录
    :return: 项目根目录
    """

    # 当前文件的绝对路径
    current_file_path = os.path.abspath(__file__)
    # 获取工程的根目录，先获取当前文件所在的目录
    current_dir = os.path.dirname(current_file_path)
    # 再获取工程的根目录
    project_root = os.path.dirname(current_dir)
    return project_root


def get_abs_path(relative_path: str) -> str:
    """
    传递相对路径，获取绝对路径；自动归一化分隔符，兼容 Windows / Linux
    :param relative_path: 相对路径（可使用 `/` 或 `\\`）
    :return: 当前平台风格的绝对路径
    """
    project_root = get_project_root()
    return os.path.normpath(
        os.path.join(project_root, relative_path.replace("\\", "/"))
    )


if __name__ == "__main__":
    print(get_abs_path("utils/path_tool.py"))

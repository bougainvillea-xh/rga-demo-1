r"""file_handler
@Time: 2026-03-27 15:40
@File: utils\file_handler.py
"""

import hashlib
import os

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

from utils.logger_handler import logger


# 获取文件的MD5值
def get_file_md5_hex(file_path: str) -> str:
    """
    获取文件的MD5值
    :param file_path: 文件路径
    :return: MD5值
    """
    if not os.path.exists(file_path):
        logger.error(f"[md5计算] 文件不存在: {file_path}")
        return ""
    if not os.path.isfile(file_path):
        logger.error(f"[md5计算] 路径不是文件: {file_path}")
        return ""

    md5_obj = hashlib.md5()

    chunk_size = 4 * 1024  # 4KB分片, 避免文件过大撑爆内存

    try:
        with open(file_path, "rb") as f:  # 计算md5必须二进制读取
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
        """
        chunk = f.read(chunk_size)
        while chunk:
            md5_obj.update(chunk)
            chunk = f.read(chunk_size)
        """
        md5_hex = md5_obj.hexdigest()
        return md5_hex
    except Exception as e:
        logger.error(f"[md5计算] 计算失败: {e}")
        return ""


# 文件夹内的文件列表 (允许的文件后缀)
def listdir_with_allowed_type(
    path: str, allowed_types: tuple[str, ...]
) -> tuple[str, ...]:
    """
    获取文件夹内的文件列表 (允许的文件后缀)
    :param path: 文件夹路径
    :param allowed_types: 允许的文件后缀
    :return: 文件列表
    """
    files = []

    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type] 路径不是文件夹: {path}")
        return ()
    for f in os.listdir(path):
        if f.endswith(allowed_types):
            files.append(os.path.join(path, f))

    return tuple(files)


# PDF文件加载器
def pdf_loader(file_path: str, password: str | None = None) -> list[Document]:
    """
    PDF文件加载器
    :param file_path: 文件路径
    :param password: 密码
    :return: 文件内容
    """
    return PyPDFLoader(file_path, password=password).load()


# 文本文件加载器
def txt_loader(file_path: str) -> list[Document]:
    """
    文本文件加载器
    :param file_path: 文件路径
    :return: 文件内容
    """
    return TextLoader(file_path).load()

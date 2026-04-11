r"""vector_store
@Time: 2026-03-27 17:36
@File: rag\vector_store.py
"""

import os

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter

from model.factory import embed_model
from utils.config_handler import chroma_config
from utils.file_handler import (
    get_file_md5_hex,
    listdir_with_allowed_type,
    pdf_loader,
    txt_loader,
)
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


class VectorStoreService:
    def __init__(self) -> None:
        self.vector_store = Chroma(
            collection_name=chroma_config["collection_name"],
            embedding_function=embed_model,
            persist_directory=chroma_config["persist_directory"],
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_config["chunk_size"],
            chunk_overlap=chroma_config["chunk_overlap"],
            separators=chroma_config["separators"],
            length_function=len,
        )

    def get_retriever(self) -> VectorStoreRetriever:
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_config["k"]})

    def load_document(self) -> None:
        """
        从数据文件夹中加载文档, 转为向量存入向量数据库
        要计算文件的md5值做去重处理
        :return: None
        """

        def check_md5_hex(md5_for_check: str) -> bool:
            # 获取md5文件路径
            md5_hex_store_path = get_abs_path(chroma_config["md5_hex_store"])
            if not os.path.exists(md5_hex_store_path):
                # 创建md5文件
                open(md5_hex_store_path, "w", encoding="utf-8").close()
                return False  # md5没处理过

            with open(md5_hex_store_path, encoding="utf-8") as f:
                for line in f.readlines():  # 逐行读取
                    line = line.strip()  # 去除空格和换行符
                    if line == md5_for_check:
                        return True  # md5已处理过
            return False  # md5未处理过

        def save_md5_hex(md5_for_check: str) -> None:
            md5_hex_store_path = get_abs_path(chroma_config["md5_hex_store"])
            with open(md5_hex_store_path, "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")

        def get_file_documents(file_path: str) -> list[Document]:
            if file_path.endswith("txt"):
                return txt_loader(file_path)
            elif file_path.endswith("pdf"):
                return pdf_loader(file_path)
            else:
                return []

        allowed_files_path = listdir_with_allowed_type(
            get_abs_path(chroma_config["data_path"]),
            tuple(chroma_config["allow_knowledge_file_type"]),
        )

        for path in allowed_files_path:
            # 获取文件的md5值
            md5_hex = get_file_md5_hex(path)

            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库] 文件内容已存在知识库中, 跳过: {path}")
                continue

            try:
                documents = get_file_documents(path)

                if not documents:
                    logger.error(f"[加载知识库] 文件内容无效，跳过: {path}")
                    continue
                split_document = self.splitter.split_documents(documents)

                if not split_document:
                    logger.error(f"[加载知识库] 分片后无有效内容，跳过: {path}")
                    continue

                # 将内容存入向量数据库
                self.vector_store.add_documents(split_document)

                # 记录已处理过的文件的md5值, 避免下次重复处理
                save_md5_hex(md5_hex)

                logger.info(f"[加载知识库] 内容加载成功: {path}")
            except Exception as e:
                # exc_info=True 会详细记录堆栈信息, False 仅记录报错信息
                logger.error(f"[加载知识库] 内容加载失败: {str(e)}", exc_info=True)
                continue


if __name__ == "__main__":
    vs = VectorStoreService()

    vs.load_document()

    retriever = vs.get_retriever()

    res = retriever.invoke("迷路")
    for i in res:
        print(i.page_content)
        print("-" * 20)

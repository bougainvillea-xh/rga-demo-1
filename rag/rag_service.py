r"""rag_service
@Time: 2026-04-12 18:01
@File: rag\rag_service.py
@Description: 总结服务类: 用户提问->检索知识库->将检索结果与用户问题提交给模型->返回总结
结果
"""

from typing import Any

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompt_values import PromptValue
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable

from model.factory import chat_model
from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts


def print_prompt(prompt: PromptValue) -> PromptValue:
    print("=" * 50)
    print(prompt.to_string())
    print("=" * 50)
    return prompt


class RagSummarizeService:
    def __init__(self) -> None:
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()

    def _init_chain(self) -> Runnable[Any, str]:
        chart = self.prompt_template | print_prompt | self.model | StrOutputParser()
        return chart

    def retriever_docs(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)

    def rag_summarize(self, query: str) -> str:
        context_docs = self.retriever_docs(query)

        context = ""
        counter = 0
        for doc in context_docs:
            counter += 1
            context += (
                f"[参考资料{counter}]:"
                f"参考资料: {doc.page_content} | 参考元数据: {doc.metadata} \n"
            )

        return self.chain.invoke(
            {
                "input": query,
                "context": context,
            }
        )


if __name__ == "__main__":
    rag = RagSummarizeService()

    print(rag.rag_summarize("小户型适合哪些扫拖机器人"))

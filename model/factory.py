r"""factory
@Time: 2026-03-27 17:48
@File: model\factory.py
"""

import os
from abc import ABC, abstractmethod
from typing import cast

from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from pydantic import SecretStr

from utils.config_handler import rag_config

API_KEY = os.environ["API_KEY"]


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Embeddings | BaseChatModel:
        pass


class ChatModelFactory(BaseModelFactory):
    def generator(self) -> BaseChatModel:
        return ChatTongyi(
            model=rag_config["chat_model_name"],
            api_key=cast(SecretStr, API_KEY),
        )


class EmbeddingsFactory(BaseModelFactory):
    def generator(self) -> Embeddings:
        return DashScopeEmbeddings(
            model=rag_config["embeddings_model_name"],
            dashscope_api_key=API_KEY,
        )


chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()


if __name__ == "__main__":
    from langchain_core.messages import HumanMessage

    vec = embed_model.embed_query("ping")
    print(f"embed ok, dim={len(vec)}")
    msg = chat_model.invoke([HumanMessage(content="请只回复：ok")])
    print(f"chat ok: {msg.content!r}")

"""RAG 模块占位接口（P2 赛后迭代接入科室知识库）。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class RetrievalChunk:
    text: str
    source: str
    score: float = 0.0


class RAGRetriever(Protocol):
    """向量检索接口；完整实现待接入 Embedding + 向量库。"""

    def retrieve(self, query: str, *, top_k: int = 5) -> list[RetrievalChunk]: ...


class StubRAGRetriever:
    """无知识库时的空实现，Skill Runtime 可安全调用。"""

    def retrieve(self, query: str, *, top_k: int = 5) -> list[RetrievalChunk]:
        return []


def get_rag_retriever() -> RAGRetriever:
    return StubRAGRetriever()

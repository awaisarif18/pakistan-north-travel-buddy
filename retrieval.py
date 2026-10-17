"""Keyword retrieval and rank fusion over existing Chroma passages."""

from typing import Any
import re

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from rank_bm25 import BM25Okapi

SETTINGS = {"bm25_k1": 1.5, "bm25_b": 0.75, "bm25_epsilon": 0.25,
            "tokenizer": "unicode-alphanumeric-casefold-v1", "stopwords": False,
            "rrf_constant": 60, "candidate_k": 20, "weights": [1, 1],
            "tie_break": "chunk_id", "lexical_positive_scores_only": True}


def tokenize(text):
    return re.findall(r"[^\W_]+", text.casefold())


def stored_documents(collection):
    stored = collection.get(include=["documents", "metadatas"])
    documents = [Document(id=cid, page_content=text, metadata=metadata)
                 for cid, text, metadata in zip(stored["ids"], stored["documents"], stored["metadatas"])]
    if len({d.id for d in documents}) != len(documents) or any(not d.id or not d.page_content for d in documents):
        raise ValueError("Stored passages must have unique IDs and nonempty text.")
    return sorted(documents, key=lambda d: d.id)


class KeywordRetriever(BaseRetriever):
    documents: list[Document]
    index: Any
    k: int = 5

    def _get_relevant_documents(self, query, *, run_manager):
        scores = self.index.get_scores(tokenize(query))
        order = sorted(range(len(self.documents)), key=lambda i: (-float(scores[i]), self.documents[i].id))
        return [self.documents[i] for i in order if scores[i] > 0][:self.k]


def keyword_retriever(collection, k):
    documents = stored_documents(collection)
    if not documents or k < 1:
        raise ValueError("Keyword retrieval requires stored passages and k >= 1.")
    index = BM25Okapi([tokenize(d.page_content) for d in documents], k1=SETTINGS["bm25_k1"],
                     b=SETTINGS["bm25_b"], epsilon=SETTINGS["bm25_epsilon"])
    return KeywordRetriever(documents=documents, index=index, k=k)


def reciprocal_rank_fusion(rankings, k, constant=60):
    scores, documents = {}, {}
    for ranking in rankings:
        seen = set()
        for rank, document in enumerate(ranking, 1):
            if not document.id:
                raise ValueError("RRF requires the original chunk ID.")
            if document.id in seen:
                continue
            seen.add(document.id)
            documents[document.id] = document
            scores[document.id] = scores.get(document.id, 0.0) + 1.0 / (constant + rank)
    return [documents[cid] for cid in sorted(scores, key=lambda cid: (-scores[cid], cid))[:k]]


class HybridRetriever(BaseRetriever):
    dense: BaseRetriever
    keyword: BaseRetriever
    k: int = 5

    def _get_relevant_documents(self, query, *, run_manager):
        config = {"callbacks": run_manager.get_child()}
        rankings = [self.dense.invoke(query, config=config), self.keyword.invoke(query, config=config)]
        return reciprocal_rank_fusion(rankings, self.k, SETTINGS["rrf_constant"])

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

import chromadb as cdb
import dotenv
from langchain_openai import OpenAIEmbeddings


dotenv.load_dotenv()


def _default_storage_path() -> str:
    """Return on-disk location for the Chroma persistent client."""

    env_path = os.getenv("VECTOR_DB_PATH")
    if env_path:
        return env_path

    project_root = Path(__file__).resolve().parent.parent
    storage_dir = project_root / "data" / "chroma"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return str(storage_dir)


class VectorDB:
    """Light wrapper around a persistent Chroma collection."""

    def __init__(
        self,
        *,
        collection_name: str = "me_profile",
        persist_directory: Optional[str] = None,
        embedding_model: Optional[OpenAIEmbeddings] = None,
    ) -> None:
        self.persist_directory = persist_directory or _default_storage_path()
        self.client = cdb.PersistentClient(path=self.persist_directory)

        try:
            self.collection = self.client.get_or_create_collection(collection_name)
        except Exception:
            # Fallback for older Chroma versions
            self.collection = self.client.create_collection(collection_name)

        self.embedding_model = embedding_model or OpenAIEmbeddings(
            model="text-embedding-3-large",
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    # ------------------------------------------------------------------
    # Document ingestion helpers
    # ------------------------------------------------------------------
    def add_documents(
        self,
        documents: Sequence[str],
        *,
        metadatas: Optional[Sequence[dict[str, Any]]] = None,
        ids: Optional[Sequence[str]] = None,
        embeddings: Optional[Sequence[Sequence[float]]] = None,
    ) -> None:
        """Add documents to the Chroma collection."""

        documents = list(documents)
        if not documents:
            return

        count = len(documents)

        if metadatas is None:
            metadatas = [{} for _ in range(count)]
        if ids is None:
            ids = [f"doc_{i}" for i in range(count)]

        if embeddings is None:
            embeddings = self.embedding_model.embed_documents(list(documents))

        self.collection.add(
            documents=documents,
            metadatas=list(metadatas),
            ids=list(ids),
            embeddings=list(embeddings),
        )

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def query(
        self,
        query_texts: Iterable[str],
        *,
        k: int = 5,
        include: Optional[Sequence[str]] = None,
    ) -> dict[str, Any]:
        """Query the collection with one or more natural-language strings."""

        if isinstance(query_texts, str):
            query_texts = [query_texts]
        else:
            query_texts = list(query_texts)

        if not query_texts:
            raise ValueError("query_texts must contain at least one string")

        query_embeddings = self.embedding_model.embed_documents(list(query_texts))

        return self.collection.query(
            query_texts=list(query_texts),
            query_embeddings=list(query_embeddings),
            n_results=k,
            include=include,
        )

    # ------------------------------------------------------------------
    # Thin wrappers around underlying collection methods
    # ------------------------------------------------------------------
    def upsert(
        self,
        documents: Sequence[str],
        *,
        metadatas: Optional[Sequence[dict[str, Any]]] = None,
        ids: Optional[Sequence[str]] = None,
        embeddings: Optional[Sequence[Sequence[float]]] = None,
    ) -> None:
        if embeddings is None:
            embeddings = self.embedding_model.embed_documents(list(documents))
        self.collection.upsert(
            documents=list(documents),
            metadatas=list(metadatas) if metadatas is not None else None,
            ids=list(ids) if ids is not None else None,
            embeddings=list(embeddings),
        )

    def delete(self, ids: Sequence[str]) -> None:
        self.collection.delete(ids=list(ids))

    def update(
        self,
        ids: Sequence[str],
        documents: Optional[Sequence[str]] = None,
        metadatas: Optional[Sequence[dict[str, Any]]] = None,
        embeddings: Optional[Sequence[Sequence[float]]] = None,
    ) -> None:
        if documents is not None and embeddings is None:
            embeddings = self.embedding_model.embed_documents(list(documents))
        self.collection.update(
            ids=list(ids),
            documents=list(documents) if documents is not None else None,
            metadatas=list(metadatas) if metadatas is not None else None,
            embeddings=list(embeddings) if embeddings is not None else None,
        )

    def get(self, ids: Sequence[str]) -> dict[str, Any]:
        return self.collection.get(ids=list(ids))

    def count(self) -> int:
        return self.collection.count()

    def list(self) -> list[str]:
        return self.collection.list()

    def delete_all(self) -> None:
        self.collection.delete()

    def get_all(self) -> dict[str, Any]:
        return self.collection.get()

    def get_all_metadata(self) -> list[dict[str, Any]]:
        return self.collection.get(include=["metadatas"])  # type: ignore[return-value]

    def get_all_ids(self) -> list[str]:
        return self.collection.get(include=["ids"]).get("ids", [])  # type: ignore[assignment]

    def get_all_texts(self) -> list[str]:
        return self.collection.get(include=["documents"]).get("documents", [])  # type: ignore[assignment]

    def get_all_embeddings(self) -> list[list[float]]:
        return self.collection.get(include=["embeddings"]).get("embeddings", [])  # type: ignore[assignment]
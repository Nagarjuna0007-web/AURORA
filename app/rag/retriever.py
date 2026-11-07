from typing import List, Dict

from app.rag.embeddings import EmbeddingModel
from app.vectorstore.faiss_store import FAISSStore


class Retriever:
    """
    Retrieves relevant documents from the vector store.
    """

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: FAISSStore,
    ):
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        k: int = 3,
    ) -> List[Dict]:
        """
        Retrieve the most relevant documents for a query.
        """

        query_embedding = self.embedding_model.embed_query(query)

        results = self.vector_store.search(
            query_embedding,
            k=k,
        )

        return results
from typing import List


class EmbeddingModel:
    """
    Base abstraction for converting text into vector embeddings.
    """

    def embed(self, text: str) -> List[float]:
        """
        Convert text into an embedding vector.
        """
        raise NotImplementedError

    def embed_query(self, query: str) -> List[float]:
        """
        Convert a query into an embedding vector.
        """
        return self.embed(query)

    def embed_documents(
        self,
        documents: List[str]
    ) -> List[List[float]]:
        """
        Convert multiple documents into embedding vectors.
        """
        return [self.embed(document) for document in documents]
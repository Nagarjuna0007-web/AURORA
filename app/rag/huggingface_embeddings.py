from typing import List

from app.rag.embeddings import EmbeddingModel


class HuggingFaceEmbeddingModel(EmbeddingModel):
    """
    Embedding implementation using HuggingFace models.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name

        from langchain_huggingface import HuggingFaceEmbeddings

        self.model = HuggingFaceEmbeddings(
            model_name=model_name
        )

    def embed(self, text: str) -> List[float]:
        return self.model.embed_query(text)

    def embed_documents(
        self,
        documents: List[str]
    ) -> List[List[float]]:
        return self.model.embed_documents(documents)
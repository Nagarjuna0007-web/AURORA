from typing import List

from app.rag.embeddings import EmbeddingModel

BATCH_SIZE = 32


class OllamaEmbeddingModel(EmbeddingModel):
    """
    Embedding implementation that uses a model served by Ollama
    (for example ``nomic-embed-text``).

    It needs no PyTorch, which avoids heavy dependencies and Windows
    Application Control blocks on torch DLLs. Pull the model once with:
        ollama pull nomic-embed-text
    """

    def __init__(self, model_name: str, client=None):
        self.model_name = model_name

        if client is None:
            import ollama

            client = ollama.Client()

        self.client = client

    def _embed(self, inputs):
        try:
            response = self.client.embed(
                model=self.model_name,
                input=inputs,
            )
        except Exception as exc:
            if "not found" in str(exc).lower():
                raise RuntimeError(
                    f"Embedding model '{self.model_name}' is not installed. "
                    f"Run: ollama pull {self.model_name}"
                ) from exc
            raise

        vectors = response["embeddings"]

        if not vectors or not vectors[0]:
            raise RuntimeError(
                f"Ollama returned no embeddings for '{self.model_name}'."
            )

        return [list(vector) for vector in vectors]

    def embed(self, text: str) -> List[float]:
        return self._embed(text)[0]

    def embed_documents(
        self,
        documents: List[str],
    ) -> List[List[float]]:
        vectors: List[List[float]] = []

        for start in range(0, len(documents), BATCH_SIZE):
            vectors.extend(
                self._embed(documents[start:start + BATCH_SIZE])
            )

        return vectors

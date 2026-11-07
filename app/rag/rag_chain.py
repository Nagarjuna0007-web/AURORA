from app.rag.retriever import Retriever
from app.models.ollama_model import OllamaModel


class RAGChain:
    """
    Combines document retrieval with LLM generation.
    """

    def __init__(
        self,
        retriever: Retriever,
        model: OllamaModel,
    ):
        self.retriever = retriever
        self.model = model

    def answer(
        self,
        query: str,
        k: int = 3,
    ) -> str:
        """
        Retrieve relevant documents and generate
        a grounded answer using the retrieved context.
        """

        results = self.retriever.retrieve(
            query,
            k=k,
        )

        if not results:
            return "I could not find relevant information."

        context = "\n\n".join(
            result["document"]
            for result in results
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "Answer the user's question using only "
                    "the provided context. "
                    "If the answer is not present in the context, "
                    "say that there is not enough information."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Context:\n{context}\n\n"
                    f"Question:\n{query}"
                ),
            },
        ]

        return self.model.generate(messages)
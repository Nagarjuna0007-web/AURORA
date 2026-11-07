from app.rag.embeddings import EmbeddingModel

DEFAULT_MODELS = {
    "ollama": "nomic-embed-text",
    "huggingface": "sentence-transformers/all-MiniLM-L6-v2",
}


def build_embedding_model(
    provider: str = "ollama",
    model_name: str | None = None,
) -> EmbeddingModel:
    """
    Create an embedding model.

    provider: "ollama" (default, no PyTorch needed) or "huggingface"
    (needs: pip install -r requirements-hf.txt).
    """

    provider = (provider or "ollama").strip().lower()

    if provider not in DEFAULT_MODELS:
        raise ValueError(
            f"Unknown EMBEDDING_PROVIDER '{provider}'. "
            f"Use one of: {', '.join(DEFAULT_MODELS)}"
        )

    model_name = model_name or DEFAULT_MODELS[provider]

    if provider == "huggingface":
        from app.rag.huggingface_embeddings import (
            HuggingFaceEmbeddingModel,
        )

        return HuggingFaceEmbeddingModel(model_name)

    from app.rag.ollama_embeddings import OllamaEmbeddingModel

    return OllamaEmbeddingModel(model_name)

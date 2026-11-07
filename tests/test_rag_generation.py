from app.rag.huggingface_embeddings import HuggingFaceEmbeddingModel
from app.vectorstore.faiss_store import FAISSStore

from app.rag.rag_generator import RAGGenerator
from app.models.ollama_model import OllamaModel


def main():

    documents = [
        "Python is a high-level programming language.",
        "Machine learning allows computers to learn from data.",
        "Artificial intelligence enables machines to perform tasks "
        "that normally require human intelligence.",
        "FAISS is a library for efficient similarity search.",
    ]

    # -----------------------------
    # Embeddings
    # -----------------------------

    embedding_model = HuggingFaceEmbeddingModel(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    embeddings = embedding_model.embed_documents(documents)

    dimension = len(embeddings[0])

    # -----------------------------
    # Vector store
    # -----------------------------

    store = FAISSStore(dimension=dimension)

    store.add(
        embeddings,
        documents
    )

    # -----------------------------
    # Retriever
    # -----------------------------

    query = "What is Python?"

    query_embedding = embedding_model.embed(query)

    results = store.search(
        query_embedding,
        k=2
    )

    # -----------------------------
    # LLM
    # -----------------------------

    model = OllamaModel()

    generator = RAGGenerator(model)

    # -----------------------------
    # Generate answer
    # -----------------------------

    answer = generator.generate(
        query,
        results
    )

    print("\n========== RAG ANSWER ==========\n")
    print("Question:", query)
    print("\nAnswer:")
    print(answer)


if __name__ == "__main__":
    main()
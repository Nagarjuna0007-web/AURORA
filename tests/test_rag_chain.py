from app.rag.huggingface_embeddings import HuggingFaceEmbeddingModel
from app.vectorstore.faiss_store import FAISSStore
from app.rag.retriever import Retriever
from app.rag.rag_chain import RAGChain
from app.models.ollama_model import OllamaModel


def main():

    documents = [
        "Python is a high-level programming language.",
        "Machine learning allows computers to learn from data.",
        "FAISS is a library for efficient similarity search.",
        "The Earth revolves around the Sun.",
    ]

    # -----------------------------
    # Embedding model
    # -----------------------------

    embedding_model = HuggingFaceEmbeddingModel(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # -----------------------------
    # Generate document embeddings
    # -----------------------------

    embeddings = embedding_model.embed_documents(
        documents
    )

    dimension = len(embeddings[0])

    # -----------------------------
    # Vector store
    # -----------------------------

    vector_store = FAISSStore(
        dimension=dimension
    )

    vector_store.add(
        embeddings,
        documents
    )

    # -----------------------------
    # Retriever
    # -----------------------------

    retriever = Retriever(
        embedding_model=embedding_model,
        vector_store=vector_store,
    )

    # -----------------------------
    # LLM
    # -----------------------------

    model = OllamaModel()

    # -----------------------------
    # RAG Chain
    # -----------------------------

    rag_chain = RAGChain(
        retriever=retriever,
        model=model,
    )

    # -----------------------------
    # Question
    # -----------------------------

    query = "What is Python?"

    print("\n========== RAG CHAIN ==========\n")

    print(f"Question: {query}\n")

    answer = rag_chain.answer(
        query,
        k=2
    )

    print("Answer:")
    print(answer)

    print("\n===============================\n")


if __name__ == "__main__":
    main()
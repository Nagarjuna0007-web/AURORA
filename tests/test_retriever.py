from app.rag.huggingface_embeddings import HuggingFaceEmbeddingModel
from app.vectorstore.faiss_store import FAISSStore
from app.rag.retriever import Retriever


def main():

    documents = [
        "Python is a high-level programming language.",
        "Machine learning allows computers to learn from data.",
        "FAISS is a library for efficient similarity search.",
        "The Earth revolves around the Sun.",
    ]

    # Create embedding model
    embedding_model = HuggingFaceEmbeddingModel(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Generate document embeddings
    embeddings = embedding_model.embed_documents(documents)

    # Create vector store
    dimension = len(embeddings[0])

    vector_store = FAISSStore(
        dimension=dimension
    )

    # Store documents
    vector_store.add(
        embeddings,
        documents
    )

    # Create retriever
    retriever = Retriever(
        embedding_model=embedding_model,
        vector_store=vector_store,
    )

    # Test query
    query = "What is Python?"

    results = retriever.retrieve(
        query,
        k=2
    )

    print("\n========== RETRIEVER ==========\n")

    print(f"Query: {query}\n")

    for index, result in enumerate(results, start=1):

        print(f"Result {index}:")
        print(f"Document: {result['document']}")
        print(f"Distance: {result['distance']}")

        print("\n----------------------------")


if __name__ == "__main__":
    main()
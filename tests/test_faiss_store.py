from app.rag.huggingface_embeddings import HuggingFaceEmbeddingModel
from app.vectorstore.faiss_store import FAISSStore


def main():

    embedding_model = HuggingFaceEmbeddingModel(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    documents = [
        "Python is a programming language.",
        "Machine learning allows computers to learn from data.",
        "FAISS is a library for efficient similarity search.",
        "The Earth revolves around the Sun.",
    ]

    embeddings = embedding_model.embed_documents(documents)

    dimension = len(embeddings[0])

    store = FAISSStore(
        dimension=dimension
    )

    store.add(
        embeddings,
        documents
    )

    print("Stored vectors:", store.count())
    print("Vector dimensions:", dimension)

    query = "What is Python?"

    query_embedding = embedding_model.embed(query)

    results = store.search(
        query_embedding,
        k=2
    )

    print("\nQuery:", query)
    print("\nSearch Results:")

    for result in results:
        print(
            f"Document: {result['document']}"
        )

        print(
            f"Distance: {result['distance']}"
        )


if __name__ == "__main__":
    main()
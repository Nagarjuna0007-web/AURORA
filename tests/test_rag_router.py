from app.rag.rag_router import RAGRouter


def main():

    router = RAGRouter()

    test_queries = [
        "What is Python?",
        "Explain machine learning",
        "What is artificial intelligence?",
        "What is FAISS?",
        "Hello Aurora",
        "How are you?"
        "Can you tell me about Python?",
        "Can you explain FAISS?",
        "How does machine learning work?",
        "Tell me about artificial intelligence",
        "What do you know about Python?",
        "Do you like Python?",
        "Write a Python program",
        "Python",
        "machine learning",
    ]

    print("\n========== RAG ROUTER TEST ==========\n")

    for query in test_queries:

        use_rag = router.should_use_rag(query)

        print(f"Query    : {query}")
        print(f"Use RAG  : {use_rag}")
        print()


if __name__ == "__main__":
    main()
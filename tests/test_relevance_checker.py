from app.rag.relevance_checker import RelevanceChecker


def main():
    checker = RelevanceChecker(max_distance=1.0)

    retrieved_documents = [
        {
            "document": "Python is a programming language.",
            "distance": 0.25,
        },
        {
            "document": "Machine learning uses algorithms to learn from data.",
            "distance": 0.75,
        },
        {
            "document": "The weather is sunny today.",
            "distance": 1.80,
        },
    ]

    filtered_documents = checker.filter_documents(
        retrieved_documents
    )

    print("\nRelevant Documents:")
    
    for document in filtered_documents:
        print(
            f"Distance: {document['distance']:.4f} | "
            f"{document['document']}"
        )


if __name__ == "__main__":
    main()
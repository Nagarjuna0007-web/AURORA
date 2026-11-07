from app.rag.rag_evaluator import RAGEvaluator


def main():

    evaluator = RAGEvaluator()

    query = "What is Python?"

    retrieved_documents = [
        {
            "document": (
                "Python is a high-level programming language."
            ),
            "distance": 0.5,
        },
        {
            "document": (
                "Machine learning allows computers "
                "to learn patterns from data."
            ),
            "distance": 0.8,
        },
    ]

    result = evaluator.evaluate(
        query,
        retrieved_documents
    )

    print("\n========== RAG EVALUATION ==========\n")

    print(
        f"Total Retrieved: "
        f"{result['total_retrieved']}"
    )

    print(
        f"Relevant Documents: "
        f"{result['relevant_documents']}"
    )

    print(
        f"Precision: "
        f"{result['precision']:.4f}"
    )


if __name__ == "__main__":
    main()
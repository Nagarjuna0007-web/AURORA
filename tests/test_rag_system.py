from app.models.ollama_model import OllamaModel
from app.rag.rag_system import RAGSystem


def main():

    model = OllamaModel()

    rag = RAGSystem(
        model=model,
        document_path="data/rag_test.txt",
    )

    # --------------------------------
    # Test 1: Known question
    # --------------------------------

    query = "What is Python?"

    answer = rag.generate(
        query,
        k=2,
    )

    print("\n========== RAG SYSTEM ==========\n")
    print(f"Question: {query}")
    print("\nAnswer:")
    print(answer)

    # --------------------------------
    # Test 2: Unknown question
    # --------------------------------

    query = "What is quantum teleportation?"

    answer = rag.generate(
        query,
        k=2,
    )

    print("\n========== RAG SYSTEM UNKNOWN QUERY ==========\n")
    print(f"Question: {query}")
    print("\nAnswer:")
    print(answer)


if __name__ == "__main__":
    main()
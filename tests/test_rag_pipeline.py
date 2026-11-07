from app.rag.document_loader import DocumentLoader
from app.rag.text_chunker import TextChunker
from app.rag.huggingface_embeddings import HuggingFaceEmbeddingModel
from app.rag.relevance_checker import RelevanceChecker
from app.rag.rag_generator import RAGGenerator

from app.vectorstore.faiss_store import FAISSStore
from app.models.ollama_model import OllamaModel
from app.rag.rag_evaluator import RAGEvaluator

from app.rag.query_rewriter import QueryRewriter


def main():

    # --------------------------------
    # 1. Load document
    # --------------------------------

    loader = DocumentLoader()

    text = loader.load_text(
        "data/rag_test.txt"
    )

    print("Document loaded successfully.")
    print(f"Document words: {len(text.split())}")

    # --------------------------------
    # 2. Split document into chunks
    # --------------------------------

    chunker = TextChunker(
        chunk_size=20,
        overlap=5
    )

    chunks = chunker.split(text)

    print(f"Total chunks: {len(chunks)}")

    # --------------------------------
    # 3. Generate embeddings
    # --------------------------------

    embedding_model = HuggingFaceEmbeddingModel(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    embeddings = embedding_model.embed_documents(
        chunks
    )

    dimension = len(embeddings[0])

    print(f"Vector dimensions: {dimension}")

    # --------------------------------
    # 4. Store embeddings in FAISS
    # --------------------------------

    store = FAISSStore(
        dimension=dimension
    )

    store.add(
        embeddings,
        chunks
    )

    print(f"Stored vectors: {store.count()}")

    # --------------------------------
    # 5. Search
    # --------------------------------

    query = "Explain AI?"

    query_rewriter = QueryRewriter()

    retrieval_query = query_rewriter.rewrite(
        query
    )

    query_embedding = embedding_model.embed_query(
        retrieval_query
    )

    results = store.search(
        query_embedding,
        k=2
    )

    print("\n========== RAG SEARCH ==========\n")
    print(f"Original Query: {query}")
    print(f"Retrieval Query: {retrieval_query}\n")

    for index, result in enumerate(
        results,
        start=1
    ):
        print(f"Result {index}:")
        print(f"Document: {result['document']}")
        print(f"Distance: {result['distance']}")
        print("\n----------------------------")

    # --------------------------------
    # 6. RAG Evaluation
    # --------------------------------

    evaluator = RAGEvaluator()

    evaluation = evaluator.evaluate(
        retrieval_query,
        results
    )

    print("\n========== RAG EVALUATION ==========\n")

    print(
        f"Total Retrieved: "
        f"{evaluation['total_retrieved']}"
    )

    print(
        f"Relevant Documents: "
        f"{evaluation['relevant_documents']}"
    )

    print(
        f"Retrieval Precision: "
        f"{evaluation['precision']:.4f}"
    )
    # --------------------------------
    # 7. Relevance filtering
    # --------------------------------

    checker = RelevanceChecker(
        max_distance=1.0
    )

    relevant_results = checker.filter_documents(
        results
    )

    print("\n========== RELEVANT RESULTS ==========\n")

    for index, result in enumerate(
        relevant_results,
        start=1
    ):
        print(f"Relevant Result {index}:")
        print(f"Document: {result['document']}")
        print(f"Distance: {result['distance']}")
        print("\n----------------------------")

    # --------------------------------
    # 8. Generate grounded answer
    # --------------------------------

    model = OllamaModel()

    generator = RAGGenerator(
        model=model
    )

    answer = generator.generate(
        query,
        relevant_results
    )

    print("\n========== RAG ANSWER ==========\n")
    print(answer)


if __name__ == "__main__":
    main()
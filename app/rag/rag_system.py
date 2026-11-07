import os
from app.core.logger import logger

from app.rag.document_loader import DocumentLoader
from app.rag.text_chunker import TextChunker
from app.core.config import EMBEDDING_MODEL, EMBEDDING_PROVIDER
from app.rag.embedding_factory import build_embedding_model
from app.rag.retriever import Retriever
from app.rag.query_rewriter import QueryRewriter
from app.rag.relevance_checker import RelevanceChecker
from app.rag.rag_generator import RAGGenerator

from app.vectorstore.faiss_store import FAISSStore


class RAGSystem:
    """
    Complete RAG system for AURORA.

    Handles:
    - Document loading
    - Text chunking
    - Embedding generation
    - FAISS vector storage
    - Query rewriting
    - Document retrieval
    - Relevance filtering
    - Grounded answer generation
    """

    def __init__(
        self,
        model,
        document_path: str,
        embedding_model_name: str | None = None,
        chunk_size: int = 60,
        overlap: int = 15,
    ):
        self.document_path = document_path

        logger.info("Initializing RAG system...")

        # --------------------------------------------------
        # Document Loader
        # --------------------------------------------------

        self.loader = DocumentLoader()

        # --------------------------------------------------
        # Text Chunker
        # --------------------------------------------------

        self.chunker = TextChunker(
            chunk_size=chunk_size,
            overlap=overlap,
        )

        # --------------------------------------------------
        # Embedding Model
        # --------------------------------------------------

        self.embedding_model = build_embedding_model(
            EMBEDDING_PROVIDER,
            embedding_model_name or EMBEDDING_MODEL,
        )

        # --------------------------------------------------
        # Load Document
        # --------------------------------------------------

        text = self.loader.load_text(
            document_path
        )

        logger.info(
            f"RAG document loaded: {document_path}"
        )

        # --------------------------------------------------
        # Create Chunks
        # --------------------------------------------------

        self.chunks = self.chunker.split(
            text
        )

        if not self.chunks:
            raise ValueError(
                "RAG document contains no usable text."
            )

        logger.info(
            f"Created {len(self.chunks)} document chunks."
        )

        # --------------------------------------------------
        # Generate Embeddings
        # --------------------------------------------------

        embeddings = (
            self.embedding_model.embed_documents(
                self.chunks
            )
        )

        dimension = len(
            embeddings[0]
        )

        logger.info(
            f"Embedding dimension: {dimension}"
        )

        # --------------------------------------------------
        # FAISS Vector Store
        # --------------------------------------------------

        self.vector_store = FAISSStore(
            dimension=dimension
        )

        self.vector_store.add(
            embeddings,
            self.chunks
        )

        logger.info(
            f"Stored {self.vector_store.count()} vectors."
        )

        # --------------------------------------------------
        # Retriever
        # --------------------------------------------------

        self.retriever = Retriever(
            embedding_model=self.embedding_model,
            vector_store=self.vector_store,
        )

        # --------------------------------------------------
        # Query Rewriter
        # --------------------------------------------------

        self.query_rewriter = QueryRewriter()

        # --------------------------------------------------
        # Relevance Checker
        # --------------------------------------------------

        self.relevance_checker = RelevanceChecker(
            max_distance=float(
                os.getenv("RAG_MAX_DISTANCE", "1.0")
            )
        )

        # --------------------------------------------------
        # RAG Generator
        # --------------------------------------------------

        self.generator = RAGGenerator(
            model
        )

        logger.info(
            "RAG system initialized successfully."
        )

    # ======================================================
    # RETRIEVAL
    # ======================================================

    def retrieve(
        self,
        query: str,
        k: int = 3,
    ):
        """
        Rewrite the query and retrieve candidate
        documents from the vector store.

        Relevance filtering is intentionally handled
        by generate().
        """

        rewritten_query = (
            self.query_rewriter.rewrite(
                query
            )
        )

        logger.info(
            f"RAG retrieval using rewritten query: "
            f"'{rewritten_query}'"
        )

        retrieved_documents = (
            self.retriever.retrieve(
                rewritten_query,
                k=k,
            )
        )

        return retrieved_documents

    # ======================================================
    # GENERATION
    # ======================================================

    def generate(
        self,
        query: str,
        k: int = 5,
    ):
        """
        Retrieve documents, filter them by relevance,
        and generate a grounded answer.
        """

        retrieved_documents = self.retrieve(
            query,
            k=k,
        )

        logger.info(
            f"RAG retrieved {len(retrieved_documents)} "
            f"candidate documents."
        )

        # --------------------------------------------------
        # Relevance Filtering
        # --------------------------------------------------

        relevant_documents = (
            self.relevance_checker.filter_documents(
                retrieved_documents
            )
        )

        logger.info(
            f"RAG retained {len(relevant_documents)} "
            f"relevant documents."
        )

        # --------------------------------------------------
        # Grounded Generation
        # --------------------------------------------------

        return self.generator.generate(
            query,
            relevant_documents,
        )


if __name__ == "__main__":
    pass
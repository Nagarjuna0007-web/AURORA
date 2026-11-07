import numpy as np

from app.core.logger import logger


# ======================================================
# OPTIONAL FAISS SUPPORT
# ======================================================

try:
    import faiss

    FAISS_AVAILABLE = True

    logger.info(
        "FAISS vector store available."
    )

except (ImportError, OSError) as exc:

    faiss = None
    FAISS_AVAILABLE = False

    logger.warning(
        "FAISS unavailable. "
        "Using NumPy vector search fallback. "
        f"Reason: {exc}"
    )


class FAISSStore:
    """
    Vector store for AURORA.

    Uses FAISS when available.

    If FAISS cannot be loaded because of a native
    library or operating-system restriction, the store
    automatically falls back to NumPy-based L2 search.

    The public interface remains the same so the rest of
    the RAG pipeline does not need to know which backend
    is being used.
    """

    def __init__(self, dimension):

        self.dimension = dimension

        self.documents = []

        # --------------------------------------------------
        # FAISS backend
        # --------------------------------------------------

        if FAISS_AVAILABLE:

            self.index = faiss.IndexFlatL2(
                dimension
            )

            self.vectors = None

            self.backend = "faiss"

            logger.info(
                "FAISSStore initialized using FAISS backend."
            )

        # --------------------------------------------------
        # NumPy fallback backend
        # --------------------------------------------------

        else:

            self.index = None

            self.vectors = np.empty(
                (0, dimension),
                dtype="float32"
            )

            self.backend = "numpy"

            logger.info(
                "FAISSStore initialized using "
                "NumPy fallback backend."
            )

    # ======================================================
    # ADD
    # ======================================================

    def add(self, embeddings, documents):
        """
        Add embeddings and their corresponding documents.
        """

        vectors = np.array(
            embeddings,
            dtype="float32"
        )

        if vectors.ndim != 2:
            raise ValueError(
                "Embeddings must be a 2D array."
            )

        if vectors.shape[1] != self.dimension:
            raise ValueError(
                "Embedding dimension does not match "
                "vector store dimension."
            )

        if len(vectors) != len(documents):
            raise ValueError(
                "Number of embeddings must match "
                "number of documents."
            )

        # --------------------------------------------------
        # FAISS
        # --------------------------------------------------

        if self.backend == "faiss":

            self.index.add(vectors)

        # --------------------------------------------------
        # NumPy fallback
        # --------------------------------------------------

        else:

            if len(self.vectors) == 0:

                self.vectors = vectors

            else:

                self.vectors = np.vstack(
                    [
                        self.vectors,
                        vectors
                    ]
                )

        self.documents.extend(documents)

        logger.debug(
            f"VectorStore | Added {len(vectors)} vectors "
            f"using {self.backend} backend."
        )

    # ======================================================
    # SEARCH
    # ======================================================

    def search(self, query_embedding, k=3):
        """
        Search for the most similar documents.

        Uses squared L2 distance, matching the behavior
        of FAISS IndexFlatL2.
        """

        if not self.documents:
            return []

        # Prevent requesting more results than available.
        k = min(
            k,
            len(self.documents)
        )

        query_vector = np.array(
            query_embedding,
            dtype="float32"
        )

        if query_vector.ndim != 1:
            query_vector = query_vector.reshape(-1)

        if len(query_vector) != self.dimension:
            raise ValueError(
                "Query embedding dimension does not "
                "match vector store dimension."
            )

        # --------------------------------------------------
        # FAISS SEARCH
        # --------------------------------------------------

        if self.backend == "faiss":

            query_vector = query_vector.reshape(
                1,
                -1
            )

            distances, indices = self.index.search(
                query_vector,
                k
            )

            results = []

            for distance, index in zip(
                distances[0],
                indices[0]
            ):

                if index == -1:
                    continue

                results.append(
                    {
                        "document": self.documents[index],
                        "distance": float(distance)
                    }
                )

            return results

        # --------------------------------------------------
        # NUMPY SEARCH
        # --------------------------------------------------

        differences = (
            self.vectors
            - query_vector
        )

        distances = np.sum(
            differences ** 2,
            axis=1
        )

        nearest_indices = np.argsort(
            distances
        )[:k]

        results = []

        for index in nearest_indices:

            results.append(
                {
                    "document": self.documents[index],
                    "distance": float(
                        distances[index]
                    )
                }
            )

        return results

    # ======================================================
    # COUNT
    # ======================================================

    def count(self):
        """
        Return number of stored vectors.
        """

        if self.backend == "faiss":

            return self.index.ntotal

        return len(self.documents)

    # ======================================================
    # CLEAR
    # ======================================================

    def clear(self):
        """
        Clear the vector store.
        """

        self.documents.clear()

        if self.backend == "faiss":

            self.index = faiss.IndexFlatL2(
                self.dimension
            )

        else:

            self.vectors = np.empty(
                (0, self.dimension),
                dtype="float32"
            )

        logger.debug(
            f"VectorStore | Cleared using "
            f"{self.backend} backend."
        )

    # ======================================================
    # BACKEND INFORMATION
    # ======================================================

    def get_backend(self):
        """
        Return the active vector-search backend.
        """

        return self.backend
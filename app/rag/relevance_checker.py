from app.core.logger import logger


class RelevanceChecker:
    """
    Evaluates whether retrieved documents are relevant
    enough to be used by Aurora's RAG generator.
    """

    def __init__(self, max_distance=1.0):
        self.max_distance = max_distance

    def filter_documents(self, retrieved_documents):
        """
        Keep only documents whose FAISS distance is
        within the configured relevance threshold.
        """

        if not retrieved_documents:
            logger.info(
                "Relevance Checker | No documents to evaluate."
            )
            return []

        relevant_documents = []

        for document in retrieved_documents:
            distance = document.get("distance")

            if distance is None:
                logger.warning(
                    "Relevance Checker | Document has no distance. "
                    "Rejecting document."
                )
                continue

            if distance <= self.max_distance:
                relevant_documents.append(document)

                logger.info(
                    f"Relevance Checker | Accepted document "
                    f"| Distance: {distance:.4f}"
                )

            else:
                logger.info(
                    f"Relevance Checker | Rejected document "
                    f"| Distance: {distance:.4f}"
                )

        logger.info(
            f"Relevance Checker | "
            f"Accepted: {len(relevant_documents)} / "
            f"{len(retrieved_documents)}"
        )

        return relevant_documents
import re

from app.core.logger import logger


class RAGEvaluator:
    """
    Evaluates the relevance of retrieved documents
    against a user query.
    """

    def __init__(self):
        self.stop_words = {
            "what",
            "is",
            "a",
            "an",
            "the",
            "are",
            "was",
            "were",
            "of",
            "to",
            "in",
            "on",
            "for",
            "and",
            "or",
            "do",
            "does",
            "how",
            "why",
            "can",
            "could",
        }

    def _tokenize(self, text):
        """
        Convert text into normalized word tokens.
        """

        words = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower()
        )

        return {
            word
            for word in words
            if word not in self.stop_words
        }

    def evaluate(self, query, retrieved_documents):
        """
        Calculate basic retrieval precision using
        normalized keyword overlap.
        """

        if not retrieved_documents:
            logger.info(
                "RAG Evaluator | No documents retrieved."
            )

            return {
                "total_retrieved": 0,
                "relevant_documents": 0,
                "precision": 0.0,
            }

        query_words = self._tokenize(query)

        relevant_documents = 0

        for document in retrieved_documents:

            document_words = self._tokenize(
                document["document"]
            )

            if query_words.intersection(
                document_words
            ):
                relevant_documents += 1

        total_retrieved = len(
            retrieved_documents
        )

        precision = (
            relevant_documents / total_retrieved
        )

        logger.info(
            f"RAG Evaluator | "
            f"Relevant: {relevant_documents} | "
            f"Retrieved: {total_retrieved} | "
            f"Precision: {precision:.4f}"
        )

        return {
            "total_retrieved": total_retrieved,
            "relevant_documents": relevant_documents,
            "precision": precision,
        }
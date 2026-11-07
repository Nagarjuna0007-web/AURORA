import re

from app.core.logger import logger


class QueryRewriter:
    """
    Converts user queries into retrieval-friendly queries.
    """

    def __init__(self):
        self.aliases = {
            "ml": "machine learning",
            "ai": "artificial intelligence",
            "nlp": "natural language processing",
            "nn": "neural network",
        }

    def rewrite(self, query: str) -> str:
        """
        Rewrite common abbreviations into
        knowledge-base terminology.
        """

        original_query = query.strip()

        if not original_query:
            return ""

        rewritten_query = original_query.lower()

        for alias, expanded_term in self.aliases.items():

            pattern = rf"\b{re.escape(alias)}\b"

            rewritten_query = re.sub(
                pattern,
                expanded_term,
                rewritten_query
            )

        logger.info(
            f"Query Rewriter | "
            f"Original: '{original_query}' | "
            f"Rewritten: '{rewritten_query}'"
        )

        return rewritten_query
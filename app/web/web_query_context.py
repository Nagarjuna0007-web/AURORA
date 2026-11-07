from app.core.logger import logger


class WebQueryContext:
    """
    Detects and resolves contextual web-search queries
    using previous conversation history.
    """

    def __init__(self, model=None):
        self.model = model

        self.context_indicators = {
            "it",
            "its",
            "they",
            "them",
            "their",
            "this",
            "that",
            "these",
            "those",
            "more",
            "again",
            "above",
            "previous",
            "earlier",
        }

    def is_contextual(self, query):
        """
        Determine whether the query appears to depend
        on previous conversation context.
        """

        query = query.lower().strip()

        words = set(
            query.replace("?", "").replace(",", "").split()
        )

        return bool(
            words & self.context_indicators
        )

    def get_context(self, history):
        """
        Return recent conversation messages that can
        provide context for the current query.
        """

        if not history:
            return []

        return history[-6:]

    def resolve(self, query, history):
        """
        Resolve a contextual query into a self-contained
        web-search query.
        """

        if not self.is_contextual(query):
            return query

        context = self.get_context(history)

        if not context:
            return query

        if self.model is None:
            return query

        conversation = "\n".join(
            f"{item['role']}: {item['message']}"
            for item in context
        )

        prompt = (
            "Rewrite the user's current query into a "
            "self-contained web search query.\n\n"
            "Use the previous conversation only to resolve "
            "references such as it, its, they, this, that, "
            "or similar contextual references.\n\n"
            "Do not answer the question.\n"
            "Do not explain the rewrite.\n"
            "Return only the rewritten search query.\n\n"
            f"Previous conversation:\n"
            f"{conversation}\n\n"
            f"Current query:\n"
            f"{query}"
        )

        logger.info(
            "Resolving contextual web search query."
        )

        rewritten_query = self.model.generate(
            [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )

        rewritten_query = rewritten_query.strip()

        if not rewritten_query:
            return query

        logger.info(
            f"Web Query Context | Original: '{query}' | "
            f"Resolved: '{rewritten_query}'"
        )

        return rewritten_query
import re

from app.core.logger import logger

# Topics Aurora's knowledge base (data/rag_test.txt) can answer about.
# Matching is by whole word/phrase, so "rag" does not match "storage".
KNOWLEDGE_TOPICS = {
    "python",
    "machine learning",
    "artificial intelligence",
    "deep learning",
    "neural network",
    "neural networks",
    "natural language processing",
    "nlp",
    "data science",
    "faiss",
    "fastapi",
    "ollama",
    "rag",
    "retrieval-augmented generation",
    "retrieval augmented generation",
    "large language model",
    "large language models",
    "llm",
    "llms",
    "embedding",
    "embeddings",
    "vector database",
    "vector databases",
    "transformer",
    "transformers",
    "prompt injection",
    "supervised learning",
    "unsupervised learning",
    "reinforcement learning",
    "ml",
    "dl",
    "nn",
}
# Note: the bare word "ai" is deliberately not a topic. It is ambiguous and
# often appears in current-events questions ("the current state of AI").

# Short forms mapped to the full topic name (used to rewrite follow-ups).
TOPIC_ALIASES = {
    "ml": "machine learning",
    "dl": "deep learning",
    "nn": "neural network",
    "nlp": "natural language processing",
    "llm": "large language model",
    "llms": "large language model",
    "rag": "retrieval-augmented generation",
}

KNOWLEDGE_INTENTS = {
    "what is",
    "what are",
    "what's",
    "what do you know",
    "what else",
    "tell me about",
    "tell me more",
    "more about",
    "anything else",
    "elaborate",
    "describe",
    "overview",
    "explain",
    "how does",
    "how do",
    "why is",
    "why are",
    "who created",
    "who invented",
    "who made",
    "when was",
    "difference between",
    "uses of",
    "used for",
    "features of",
    "benefits of",
    "advantages of",
}

GENERATION_INTENTS = {
    "write",
    "create",
    "build",
    "generate",
    "code",
    "program",
    "make",
}


def _compile(phrases):
    ordered = sorted(phrases, key=len, reverse=True)
    pattern = "|".join(re.escape(p) for p in ordered)
    return re.compile(
        rf"(?<![a-z0-9])(?:{pattern})(?![a-z0-9])"
    )


class RAGRouter:
    """
    Determines whether a user query should use
    Aurora's knowledge base.
    """

    def __init__(self):
        self.knowledge_topics = set(KNOWLEDGE_TOPICS)
        self.knowledge_intents = set(KNOWLEDGE_INTENTS)
        self.generation_intents = set(GENERATION_INTENTS)

        self._topic_re = _compile(self.knowledge_topics)
        self._knowledge_re = _compile(self.knowledge_intents)
        self._generation_re = _compile(self.generation_intents)

    def should_use_rag(self, query: str) -> bool:
        """
        Determine whether a query should be routed
        to Aurora's knowledge base.
        """

        query = query.lower().strip()

        if not query:
            return False

        topic_match = bool(self._topic_re.search(query))

        knowledge_intent_match = bool(
            self._knowledge_re.search(query)
        )

        generation_intent_match = bool(
            self._generation_re.search(query)
        )

        use_rag = (
            topic_match
            and knowledge_intent_match
            and not generation_intent_match
        )

        logger.info(
            f"RAG Router | Query: '{query}' | "
            f"Topic Match: {topic_match} | "
            f"Knowledge Intent: {knowledge_intent_match} | "
            f"Generation Intent: {generation_intent_match} | "
            f"Use RAG: {use_rag}"
        )

        return use_rag

import re

from app.core.logger import logger
from app.rag.rag_router import KNOWLEDGE_TOPICS, TOPIC_ALIASES

PRONOUN_RE = re.compile(r"\b(its|it|they|them|their)\b", re.IGNORECASE)

FOLLOW_UP_PHRASES = (
    "what else",
    "tell me more",
    "anything else",
    "go on",
    "elaborate",
    "explain further",
    "more details",
    "more information",
    "more info",
    "continue",
)

# A pronoun in these requests is not about the last topic
# ("what time is it").
NOT_ABOUT_TOPIC_WORDS = {
    "time", "date", "day", "today", "tomorrow", "yesterday",
    "weather", "temperature", "clock", "hour", "hours", "raining",
}


class FollowUpResolver:
    """
    Makes follow-up questions self-contained.

    "what is python"  ->  remembers topic "python"
    "what else do you know about it"
        ->  "what else do you know about python"

    It only rewrites short follow-ups that use a pronoun (it, its, they,
    them, their) or a phrase such as "tell me more", and only while the
    remembered topic is recent.
    """

    def __init__(self, max_age: int = 4, max_words: int = 14):
        self.max_age = max_age
        self.max_words = max_words
        self.last_topic = None
        self._turns_since_topic = 0

        ordered = sorted(KNOWLEDGE_TOPICS, key=len, reverse=True)
        pattern = "|".join(re.escape(t) for t in ordered)
        self._topic_re = re.compile(
            rf"(?<![a-z0-9])(?:{pattern})(?![a-z0-9])"
        )

    def find_topic(self, text: str):
        """Return the first known topic mentioned in the text, or None."""
        match = self._topic_re.search(text.lower())

        if not match:
            return None

        topic = match.group(0)

        return TOPIC_ALIASES.get(topic, topic)

    def reset(self):
        self.last_topic = None
        self._turns_since_topic = 0

    def resolve(self, query: str) -> str:
        text = query.strip()

        if not text:
            return query

        topic = self.find_topic(text)

        if topic:
            self.last_topic = topic
            self._turns_since_topic = 0
            return query

        if self.last_topic is None:
            return query

        self._turns_since_topic += 1

        if self._turns_since_topic > self.max_age:
            self.reset()
            return query

        lowered = text.lower()
        words = re.findall(r"[a-z0-9']+", lowered)

        if len(words) > self.max_words:
            return query

        if NOT_ABOUT_TOPIC_WORDS & set(words):
            return query

        topic = self.last_topic

        if PRONOUN_RE.search(text):
            resolved = PRONOUN_RE.sub(
                lambda m: f"{topic}'s" if m.group(1).lower() in ("its", "their") else topic,
                text,
            )
        elif any(phrase in lowered for phrase in FOLLOW_UP_PHRASES):
            if re.search(r"\babout\b", lowered):
                return query

            resolved = f"{text.rstrip('?.! ')} about {topic}"
        else:
            return query

        logger.info(
            f"Follow-up Resolver | Original: '{query}' | "
            f"Resolved: '{resolved}'"
        )

        return resolved

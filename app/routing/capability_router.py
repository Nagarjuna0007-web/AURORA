import re
from app.core.logger import logger
from app.rag.rag_router import RAGRouter


class CapabilityRouter:
    """
    Determines which capability should handle
    an incoming Aurora request.
    """

    def __init__(self, session=None):
        self.rag_router = RAGRouter()
        self.session = session

        self.calculation_indicators = {
            "+",
            "-",
            "*",
            "/",
            "%",
            "**",
        }

        self.time_indicators = {
            "what time",
            "whats the time",
            "what is the time",
            "what's the time",
            "current time",
            "time now",
            "time",
        }

        self.date_indicators = {
            "what date",
            "whats the date",
            "what is the date",
            "what's the date",
            "current date",
            "today's date",
            "todays date",
            "date today",
            "what day is today",
        }

        self.web_search_indicators = {
            "news",
            "search",
            "search for",
            "look up",
            "look it up",
            "on the web",
            "online",
            "internet",
            "who won",
        }

        self.contextual_web_indicators = {
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

        self.temporal_indicators = {
            "latest",
            "recent",
            "recently",
            "up to date",
            "up-to-date",
            "newest",
            "recent developments",
            "what happened",
        }

        self.current_information_indicators = {
            "price",
            "weather",
            "version",
            "stock",
            "score",
            "results",
            "rate",
            "exchange rate",
            "news",
            "updates",
            "developments",
        }

        # Centralized routing rules.
        # Each rule maps a capability to its detection function.
        self.routing_rules = [
            ("calculator", self._looks_like_calculation),
            ("time", self._looks_like_time_query),
            ("date", self._looks_like_date_query),
            ("web_search", self._looks_like_temporal_query),
            ("web_search", self._looks_like_web_search_query),
            ("web_search",self._looks_like_contextual_web_query),
            ("web_search", self._looks_like_current_information_query),
        ]

    def route(self, query: str) -> str:
        """
        Return the capability that should handle
        the query.
        """

        query = query.strip()

        if not query:
            return "normal"

        capability = None

        # Evaluate capabilities using centralized routing rules.
        for rule_capability, rule_checker in self.routing_rules:
            if rule_checker(query):
                capability = rule_capability
                break

        # If no direct capability matches,
        # allow the RAG router to determine whether
        # the query belongs to the knowledge system.
        if capability is None:
            if self.rag_router.should_use_rag(query):
                capability = "rag"
            else:
                capability = "normal"

        logger.info(
            f"Capability Router | "
            f"Query: '{query}' | "
            f"Capability: {capability}"
        )

        return capability

    def _looks_like_calculation(
        self,
        query: str,
    ) -> bool:
        """
        Determine whether a query appears to contain
        a mathematical expression.
        """

        query = query.strip()

        return any(
            operator in query
            for operator in self.calculation_indicators
        )

    def _looks_like_time_query(
        self,
        query: str,
    ) -> bool:
        """
        Determine whether a query is asking for
        the current time.
        """

        query = query.lower().strip()

        # Bare "time" is a valid direct request.
        if query == "time":
            return True

        # For longer queries, require a meaningful time-related phrase.
        return any(
            re.search(
                rf"\b{re.escape(indicator)}\b",
                query,
            )
            for indicator in self.time_indicators
            if indicator != "time"
        )
        
    def _looks_like_date_query(
        self,
        query: str,
    ) -> bool:
        """
        Determine whether a query is asking for
        the current date.
        """

        query = query.lower().strip()

        return any(
            indicator in query
            for indicator in self.date_indicators
        )

    def _looks_like_temporal_query(self, query: str) -> bool:
        query = query.lower().strip()

        return any(
            re.search(
                rf"\b{re.escape(indicator)}\b",
                query,
            )
            for indicator in self.temporal_indicators
        )

    def _looks_like_current_information_query(
        self,
        query: str,
    ) -> bool:
        """
        Determine whether a query asks for current
        information about a freshness-sensitive subject.
        """

        query = query.lower().strip()

        if "current" not in query:
            return False

        return any(
            re.search(
                rf"\b{re.escape(indicator)}\b",
                query,
            )
            for indicator in self.current_information_indicators
        )
    
    def _looks_like_web_search_query(
            self,
            query: str,
        ) -> bool:
            """
            Determine whether a query appears to require
            current or web-based information.
            """

            query = query.lower().strip()

            return any(
                indicator in query
                for indicator in self.web_search_indicators
            )

    def _looks_like_contextual_web_query(
        self,
        query: str,
    ) -> bool:
        """
        Determine whether a query appears to be a
        contextual follow-up to a previous conversation.
        """

        if self.session is None:
            return False

        history = self.session.get_history()

        if not history:
            return False

        query = query.lower().strip()

        words = set(
            query.replace("?", "")
            .replace(",", "")
            .split()
        )

        if not words & self.contextual_web_indicators:
            return False

        # A contextual query should only be routed to web
        # search when the previous conversation involved
        # a web search.
        recent_history = history[-6:]

        return any(
            item.get("role") == "User"
            and any(
                indicator in item.get(
                    "message",
                    ""
                ).lower()
                for indicator in self.web_search_indicators
            )
            for item in recent_history
        )
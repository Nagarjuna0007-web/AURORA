from app.core.logger import logger
from app.rag.follow_up_resolver import FollowUpResolver


class CapabilityOrchestrator:
    """
    Coordinates multiple AURORA capabilities for a
    single user request.

    The orchestrator sits above the Capability Router
    and Capability Executor.

    Responsibilities:
    - Detect whether a request needs multiple capabilities.
    - Select the required capabilities.
    - Detect multiple intents within one request.
    - Prioritize current/web information for temporal queries.
    - Execute each capability through the existing executor.
    - Preserve streaming for single-capability requests.
    - Return structured results for later synthesis.
    """

    def __init__(
        self,
        router,
        executor,
        resolver=None,
    ):
        self.router = router
        self.executor = executor
        self.resolver = resolver or FollowUpResolver()

    def orchestrate(
        self,
        message: str,
        stream: bool = False,
        stream_events: bool = False,
    ):
        message = message.strip()

        if not message:
            return {
                "capabilities": [],
                "results": [],
            }

        # Make follow-ups such as "what else do you know about it"
        # self-contained before routing and execution.
        message = self.resolver.resolve(message)

        capabilities = self._determine_capabilities(
            message
        )

        logger.info(
            f"Capability Orchestrator | "
            f"Capabilities: {capabilities}"
        )

        results = []

        # --------------------------------------------------
        # Single Capability
        # --------------------------------------------------

        if len(capabilities) == 1:

            capability = capabilities[0]

            result = self.executor.execute(
                capability=capability,
                message=message,
                stream=stream,
                stream_events=stream_events,
            )

            results.append(
                {
                    "capability": capability,
                    "result": result,
                }
            )

            return {
                "capabilities": capabilities,
                "results": results,
            }

        # --------------------------------------------------
        # Multiple Capabilities
        # --------------------------------------------------

        for capability in capabilities:

            result = self.executor.execute(
                capability=capability,
                message=message,
                stream=False,
            )

            results.append(
                {
                    "capability": capability,
                    "result": result,
                }
            )

        return {
            "capabilities": capabilities,
            "results": results,
        }

    def _determine_capabilities(
        self,
        message: str,
    ):
        capabilities = []

        primary_capability = self.router.route(
            message
        )

        has_web_intent = (
            self._needs_web_search(message)
        )

        has_rag_intent = (
            self._needs_rag(message)
        )

        has_multiple_intents = (
            self._has_multiple_intents(message)
        )

        has_calculation = (
            self._needs_calculation(message)
        )

        # --------------------------------------------------
        # Genuine RAG + Web Multi-Intent
        # --------------------------------------------------

        if (
            has_multiple_intents
            and has_rag_intent
            and has_web_intent
        ):

            self._add_capability(
                capabilities,
                "rag",
            )

            self._add_capability(
                capabilities,
                "web_search",
            )

        # --------------------------------------------------
        # Web Only
        # --------------------------------------------------

        elif has_web_intent:

            self._add_capability(
                capabilities,
                "web_search",
            )

        # --------------------------------------------------
        # RAG Only
        # --------------------------------------------------

        elif has_rag_intent:

            self._add_capability(
                capabilities,
                "rag",
            )

        # --------------------------------------------------
        # Other Primary Capability
        # --------------------------------------------------

        elif primary_capability != "normal":

            self._add_capability(
                capabilities,
                primary_capability,
            )

        # --------------------------------------------------
        # Calculator
        # --------------------------------------------------

        if has_calculation:

            self._add_capability(
                capabilities,
                "calculator",
            )

        # --------------------------------------------------
        # Fallback
        # --------------------------------------------------

        if not capabilities:

            capabilities.append(
                primary_capability
            )

        return capabilities

    def _has_multiple_intents(
        self,
        message: str,
    ) -> bool:
        """
        Detects whether a request contains multiple
        independently answerable parts.

        The initial orchestration layer uses common
        conjunction patterns to identify compound
        questions without replacing the existing
        Capability Router.
        """

        normalized = (
            message.lower()
            .replace("?", " ? ")
        )

        compound_indicators = (
            " and ",
            " also ",
            " as well as ",
            " plus ",
        )

        return any(
            indicator in normalized
            for indicator in compound_indicators
        )

    def _needs_rag(
        self,
        message: str,
    ) -> bool:
        try:

            return self.router.rag_router.should_use_rag(
                message
            )

        except Exception:

            logger.exception(
                "RAG orchestration detection failed."
            )

            return False

    def _needs_web_search(
        self,
        message: str,
    ) -> bool:
        return (
            self.router._looks_like_temporal_query(
                message
            )
            or self.router._looks_like_web_search_query(
                message
            )
            or self.router._looks_like_contextual_web_query(
                message
            )
        )

    def _needs_calculation(
        self,
        message: str,
    ) -> bool:
        return self.router._looks_like_calculation(
            message
        )

    @staticmethod
    def _add_capability(
        capabilities,
        capability,
    ):
        if capability not in capabilities:

            capabilities.append(
                capability
            )
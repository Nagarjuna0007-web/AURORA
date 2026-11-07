from app.core.logger import logger
import time


class CapabilityExecutor:
    """
    Executes capabilities selected by the Capability Router.
    """

    def __init__(
        self,
        tool_registry,
        rag,
        assistant,
        session,
        web_answerer=None,
        web_query_context=None,
        web_intelligence=None,
        source_grounding=None,
    ):
        self.tool_registry = tool_registry
        self.rag = rag
        self.assistant = assistant
        self.session = session
        self.web_answerer = web_answerer
        self.web_query_context = web_query_context
        self.web_intelligence = web_intelligence
        self.source_grounding = source_grounding

    def execute(
        self,
        capability: str,
        message: str,
        stream: bool = False,
        stream_events: bool = False,
    ):
        logger.info(
            f"Capability Executor | Executing: {capability}"
        )

        tool = self.tool_registry.get(capability)

        # ==================================================
        # Web Search
        # ==================================================

        if capability == "web_search":

            if tool is None:
                raise ValueError(
                    "Web Search tool is not registered."
                )

            search_query = message

            # --------------------------------------------------
            # Resolve contextual web queries
            # --------------------------------------------------

            if self.web_query_context is not None:

                search_query = (
                    self.web_query_context.resolve(
                        message,
                        self.session.get_history(),
                    )
                )

            # --------------------------------------------------
            # Web Search
            # --------------------------------------------------

            search_start = time.perf_counter()

            results = tool.execute(
                search_query
            )

            search_time = (
                time.perf_counter()
                - search_start
            )

            logger.info(
                f"Web Search Timing | "
                f"Search: {search_time:.3f}s"
            )

            preparation_start = time.perf_counter()

            # --------------------------------------------------
            # Web Intelligence
            # --------------------------------------------------

            intelligence = None

            if self.web_intelligence is not None:

                intelligence = (
                    self.web_intelligence.analyze(
                        results
                    )
                )

                logger.info(
                    "Web Intelligence analysis completed."
                )

            # --------------------------------------------------
            # Source Grounding
            # --------------------------------------------------

            grounding = None

            if self.source_grounding is not None:

                grounding = (
                    self.source_grounding.ground(
                        message,
                        results,
                    )
                )

                logger.info(
                    "Source Grounding completed."
                )

            # --------------------------------------------------
            # Web Preparation Timing
            # --------------------------------------------------

            preparation_time = (
                time.perf_counter()
                - preparation_start
            )

            logger.info(
                f"Web Search Timing | "
                f"Preparation: "
                f"{preparation_time:.3f}s"
            )

            # --------------------------------------------------
            # Web Answer Generation
            # --------------------------------------------------

            if self.web_answerer is None:
                return str(results)


            # --------------------------------------------------
            # Browser/web-interface structured streaming
            # --------------------------------------------------

            if stream_events:

                logger.info(
                    "Web Search | Structured streaming enabled."
                )

                return self.web_answerer.stream_answer_events(
                    message,
                    results,
                    intelligence=intelligence,
                    grounding=grounding,
                )


            # --------------------------------------------------
            # Existing text streaming
            # --------------------------------------------------

            if stream:

                logger.info(
                    "Web Search | Streaming answer enabled."
                )

                return self.web_answerer.stream_answer(
                    message,
                    results,
                    intelligence=intelligence,
                    grounding=grounding,
                )


            # --------------------------------------------------
            # Existing complete-answer path
            # --------------------------------------------------

            answer_start = time.perf_counter()

            answer = self.web_answerer.answer(
                message,
                results,
                intelligence=intelligence,
                grounding=grounding,
            )

            answer_time = (
                time.perf_counter()
                - answer_start
            )

            logger.info(
                f"Web Search Timing | "
                f"Answer Generation: "
                f"{answer_time:.3f}s"
            )

            logger.info(
                f"Web Search Timing | "
                f"Total: "
                f"{search_time + answer_time:.3f}s"
            )

            return answer
        # ==================================================
        # Registered Tools
        # ==================================================

        if tool is not None:

            return str(
                tool.execute(message)
            )

        # ==================================================
        # RAG
        # ==================================================

        if capability == "rag":

            return self.rag.generate(
                message
            )

        # ==================================================
        # Normal Assistant Response
        # ==================================================

        if capability == "normal":

            if stream:

                return self.assistant.stream(
                    message
                )

            return self.assistant.process(
                [
                    {
                        "role": "user",
                        "content": message,
                    }
                ]
            )

        # ==================================================
        # Unknown Capability
        # ==================================================

        raise ValueError(
            f"Unknown capability: {capability}"
        )
from app.core.config import (
    APP_NAME,
    APP_VERSION,
    CONTEXT_WINDOW,
    ENVIRONMENT,
)

from app.core.logger import logger

from app.models.ollama_model import OllamaModel
from app.agents.assistant_agent import AssistantAgent

from app.session.session_manager import SessionManager
from app.memory.memory_extractor import MemoryExtractor

from app.rag.rag_system import RAGSystem
from app.routing.capability_router import CapabilityRouter

from app.tools.calculator_tool import CalculatorTool
from app.tools.time_tool import TimeTool
from app.tools.tool_registry import ToolRegistry
from app.tools.date_tool import DateTool
from app.tools.web_search_tool import WebSearchTool

from app.web.web_answerer import WebAnswerer
from app.web.web_query_context import WebQueryContext
from app.web.web_intelligence import WebIntelligence
from app.web.source_grounding import SourceGrounding

from app.execution.capability_executor import CapabilityExecutor

from app.orchestration.capability_orchestrator import (
    CapabilityOrchestrator,
)

from app.orchestration.result_synthesizer import (
    ResultSynthesizer,
)

from concurrent.futures import ThreadPoolExecutor
from threading import Timer


class AuroraEngine:

    def __init__(self):

        self.app_name = APP_NAME
        self.version = APP_VERSION
        self.environment = ENVIRONMENT

        # --------------------------------------------------
        # Session & Memory
        # --------------------------------------------------

        self.session = SessionManager()
        self.memory_extractor = MemoryExtractor()

        # --------------------------------------------------
        # Background Summary Executor
        # --------------------------------------------------

        self.summary_executor = ThreadPoolExecutor(
            max_workers=1
        )

        self._summary_scheduled_count = len(
            self.session.get_history()
        )

        # Idle-aware summary timer
        self.summary_timer = None
        self.summary_idle_seconds = 30

        logger.info("Initializing Aurora Engine...")

        # --------------------------------------------------
        # Model
        # --------------------------------------------------

        self.model = OllamaModel()

        logger.info("Model initialized.")

        # --------------------------------------------------
        # Web Query Context
        # --------------------------------------------------

        self.web_query_context = WebQueryContext(
            model=self.model
        )

        logger.info(
            "Web Query Context initialized."
        )

        # --------------------------------------------------
        # RAG System
        # --------------------------------------------------

        self.rag = RAGSystem(
            model=self.model,
            document_path="data/rag_test.txt",
        )

        logger.info("RAG system initialized.")

        # --------------------------------------------------
        # Capability Router
        # --------------------------------------------------

        self.capability_router = CapabilityRouter(
            session=self.session
        )

        logger.info(
            "Capability router initialized."
        )

        # --------------------------------------------------
        # Tool Registry
        # --------------------------------------------------

        self.tool_registry = ToolRegistry()

        logger.info(
            "Tool registry initialized."
        )

        # --------------------------------------------------
        # Calculator Tool
        # --------------------------------------------------

        self.calculator = CalculatorTool()

        self.tool_registry.register(
            self.calculator,
            capability="calculator",
        )

        logger.info(
            "Calculator tool initialized."
        )

        # --------------------------------------------------
        # Time Tool
        # --------------------------------------------------

        self.time_tool = TimeTool()

        self.tool_registry.register(
            self.time_tool,
            capability="time",
        )

        logger.info(
            "Time tool initialized."
        )

        # --------------------------------------------------
        # Date Tool
        # --------------------------------------------------

        self.date_tool = DateTool()

        self.tool_registry.register(
            self.date_tool,
            capability="date",
        )

        logger.info(
            "Date tool initialized."
        )

        # --------------------------------------------------
        # Web Search Tool
        # --------------------------------------------------

        self.web_search = WebSearchTool()

        self.tool_registry.register(
            self.web_search,
            capability="web_search",
        )

        logger.info(
            "Web Search tool initialized."
        )

        # --------------------------------------------------
        # Assistant Agent
        # --------------------------------------------------

        self.assistant = AssistantAgent(
            name="Assistant",
            model=self.model,
        )

        logger.info(
            "Assistant Agent initialized."
        )

        # --------------------------------------------------
        # Web Answerer
        # --------------------------------------------------

        self.web_answerer = WebAnswerer(
            self.assistant
        )

        logger.info(
            "Web Answerer initialized."
        )

        # --------------------------------------------------
        # Web Intelligence
        # --------------------------------------------------

        self.web_intelligence = WebIntelligence()

        logger.info(
            "Web Intelligence initialized."
        )

        # --------------------------------------------------
        # Source Grounding
        # --------------------------------------------------

        self.source_grounding = SourceGrounding()

        logger.info(
            "Source Grounding initialized."
        )

        # --------------------------------------------------
        # Capability Executor
        # --------------------------------------------------

        self.capability_executor = CapabilityExecutor(
            tool_registry=self.tool_registry,
            rag=self.rag,
            assistant=self.assistant,
            session=self.session,
            web_answerer=self.web_answerer,
            web_query_context=self.web_query_context,
            web_intelligence=self.web_intelligence,
            source_grounding=self.source_grounding,
        )

        logger.info(
            "Capability executor initialized."
        )

        # --------------------------------------------------
        # Capability Orchestrator
        # --------------------------------------------------

        self.capability_orchestrator = (
            CapabilityOrchestrator(
                router=self.capability_router,
                executor=self.capability_executor,
            )
        )

        logger.info(
            "Capability orchestrator initialized."
        )

        # --------------------------------------------------
        # Result Synthesizer
        # --------------------------------------------------

        self.result_synthesizer = (
            ResultSynthesizer(
                assistant=self.assistant
            )
        )

        logger.info(
            "Result synthesizer initialized."
        )

    # ======================================================
    # ENGINE START
    # ======================================================

    def start(self):

        logger.info("=" * 50)
        logger.info(
            f"Starting {self.app_name}"
        )
        logger.info(
            f"Version      : {self.version}"
        )
        logger.info(
            f"Environment  : {self.environment}"
        )
        logger.info("=" * 50)

        logger.info(
            "Aurora Engine Initialized Successfully."
        )

    # ======================================================
    # START BACKGROUND SUMMARY
    # ======================================================

    def _start_background_summary(
        self,
        conversation,
    ):
        """
        Start conversation summarization after
        the idle period.
        """

        logger.debug(
            "User idle period reached. "
            "Starting background summary."
        )

        self.summary_executor.submit(
            self._generate_summary_background,
            conversation,
        )

    # ======================================================
    # BACKGROUND SUMMARY
    # ======================================================

    def _generate_summary_background(
        self,
        conversation,
    ):
        """
        Generate and store the conversation summary
        without blocking the main request pipeline.
        """

        try:

            logger.debug(
                "Background conversation summary started."
            )

            summary = self.model.summarize(
                conversation
            )

            self.session.update_summary(
                summary
            )

            logger.debug(
                "Background conversation summary updated."
            )

        except Exception:

            logger.exception(
                "Background conversation summary failed."
            )

    # ======================================================
    # CONVERSATION SUMMARY
    # ======================================================

    def generate_summary_if_needed(self):
        """
        Schedule conversation summarization after
        a period of user inactivity.
        """

        history = self.session.get_history()

        # Not enough history to summarize
        if len(history) <= CONTEXT_WINDOW:
            return

        # Avoid scheduling the same history repeatedly
        if len(history) <= self._summary_scheduled_count:
            return

        old_messages = history[:-CONTEXT_WINDOW]

        if not old_messages:
            return

        conversation = "\n".join(
            f"{item['role']}: {item['message']}"
            for item in old_messages
        )

        # Mark this history as scheduled
        self._summary_scheduled_count = len(history)

        # Cancel any existing timer
        if self.summary_timer is not None:

            self.summary_timer.cancel()

        logger.debug(
            "Scheduling idle-aware conversation summary..."
        )

        # Start summary only after user inactivity
        self.summary_timer = Timer(
            self.summary_idle_seconds,
            self._start_background_summary,
            args=(conversation,),
        )

        self.summary_timer.daemon = True
        self.summary_timer.start()

    # ======================================================
    # CENTRAL REQUEST PIPELINE
    # ======================================================

    def _process_request(
        self,
        message: str,
        stream: bool = False,
    ):

        # --------------------------------------------------
        # User activity cancels pending summary timer
        # --------------------------------------------------

        if self.summary_timer is not None:

            self.summary_timer.cancel()
            self.summary_timer = None

        logger.info(
            f"User: {message}"
        )

        # --------------------------------------------------
        # Store User Message
        # --------------------------------------------------

        self.session.add_message(
            "User",
            message,
        )

        # --------------------------------------------------
        # Memory Extraction
        # --------------------------------------------------

        memories = self.memory_extractor.extract(
            message
        )

        for key, value in memories.items():

            self.session.remember(
                key,
                value,
            )

            logger.info(
                f"Remembered {key}: {value}"
            )

        # --------------------------------------------------
        # Capability Orchestration
        # --------------------------------------------------

        orchestration = (
            self.capability_orchestrator.orchestrate(
                message,
                stream=stream,
            )
        )

        capabilities = orchestration[
            "capabilities"
        ]

        capability_results = orchestration[
            "results"
        ]

        logger.info(
            f"Orchestrated capabilities: "
            f"{capabilities}"
        )

        # --------------------------------------------------
        # Result Synthesis
        # --------------------------------------------------

        if len(capability_results) > 1:

            logger.info(
                "Multiple capabilities detected. "
                "Synthesizing combined result."
            )

            response = (
                self.result_synthesizer.synthesize(
                    message,
                    capability_results,
                )
            )

        elif capability_results:

            response = capability_results[0][
                "result"
            ]

        else:

            # Safe fallback for an unexpected empty
            # orchestration result.
            response = self.assistant.process(
                [
                    {
                        "role": "user",
                        "content": message,
                    }
                ]
            )

        # --------------------------------------------------
        # Streaming Output
        # --------------------------------------------------

        if stream:

            # --------------------------------------------------
            # Normal Assistant Streaming
            # --------------------------------------------------

            if (
                len(capabilities) == 1
                and capabilities[0] == "normal"
            ):

                chunks = []

                for chunk in response:

                    print(
                        chunk,
                        end="",
                        flush=True,
                    )

                    chunks.append(chunk)

                print()

                response = "".join(
                    chunks
                )

            # --------------------------------------------------
            # Web Search Streaming
            # --------------------------------------------------

            elif (
                len(capabilities) == 1
                and capabilities[0] == "web_search"
            ):

                # WebAnswerer already handles:
                # - token streaming
                # - answer output
                # - Sources section
                #
                # Do NOT print response here.
                # Printing here would duplicate the
                # streamed web response.
                logger.debug(
                    "Web streaming handled by WebAnswerer."
                )

            # --------------------------------------------------
            # Multi-capability / synthesized response
            # --------------------------------------------------

            else:

                # Multi-capability streaming is intentionally
                # deferred until the dedicated Live Streaming
                # UI stage.
                print(
                    response,
                    flush=True,
                )

        # --------------------------------------------------
        # Store Aurora Response
        # --------------------------------------------------

        self.session.add_message(
            "Aurora",
            response,
        )

        # --------------------------------------------------
        # Schedule Idle-Aware Summary
        # --------------------------------------------------

        if self.session.should_summarize():

            self.generate_summary_if_needed()

        return response

    # ======================================================
    # CHAT
    # ======================================================

    def chat(
        self,
        message: str,
    ):

        try:

            return self._process_request(
                message,
                stream=False,
            )

        except Exception:

            logger.exception(
                "Failed to generate response."
            )

            return (
                "Sorry, something went wrong."
            )

    # ======================================================
    # STREAMING CHAT
    # ======================================================

    def stream_chat(
        self,
        message: str,
    ):

        try:

            return self._process_request(
                message,
                stream=True,
            )

        except Exception:

            logger.exception(
                "Failed to generate streaming response."
            )

            return (
                "Sorry, something went wrong."
            )

    # ======================================================
    # HISTORY
    # ======================================================

    def show_history(self):

        history = self.session.get_history()

        if not history:

            print(
                "No conversation yet."
            )

            return

        print(
            "\n========== CHAT HISTORY ==========\n"
        )

        for chat in history:

            print(
                f"{chat['role']}: "
                f"{chat['message']}\n"
            )

        print(
            "==================================\n"
        )

    # ======================================================
    # CLEAR HISTORY
    # ======================================================

    def clear_history(self):

        self.session.clear_history()

        print(
            "History cleared."
        )

    # ======================================================
    # SESSION STATISTICS
    # ======================================================

    def show_stats(self):

        print(
            "\n========== SESSION =========="
        )

        print(
            f"Total Messages : "
            f"{self.session.total_messages()}"
        )

        print(
            "=============================\n"
        )

    # ======================================================
    # MEMORY
    # ======================================================

    def show_memory(self):

        memories = self.session.get_memories()

        if not memories:

            print(
                "No memories stored."
            )

            return

        print(
            "\n========== LONG-TERM MEMORY ==========\n"
        )

        for key, value in memories.items():

            print(
                f"{key}: {value}"
            )

        print(
            "\n======================================\n"
        )

    # ======================================================
    # AVAILABLE TOOLS
    # ======================================================

    def show_tools(self):

        tools = self.tool_registry.list_tools()

        if not tools:

            print(
                "No tools registered."
            )

            return

        print(
            "\n========== AVAILABLE TOOLS ==========\n"
        )

        for tool in tools:

            print(
                f"- {tool}"
            )

        print(
            "\n=====================================\n"
        )

    # ======================================================
    # STOP
    # ======================================================

    def stop(self):

        # Cancel pending idle timer
        if self.summary_timer is not None:

            self.summary_timer.cancel()
            self.summary_timer = None

        # Shutdown summary executor
        self.summary_executor.shutdown(
            wait=False
        )

        logger.info(
            "Aurora Engine Shutdown Successfully."
        )
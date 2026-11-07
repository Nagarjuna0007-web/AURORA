import time
import re

from app.core.logger import logger


class WebAnswerer:
    """
    Generates natural-language answers using
    processed web search results, web intelligence,
    and source grounding.

    Supports both:
    - Complete answers for CLI usage.
    - Streaming answers for the web interface.
    """

    def __init__(self, assistant):
        self.assistant = assistant

        # Only the strongest results are used as the
        # primary answer-generation context.
        self.context_result_limit = 3

        # Limit snippet size to reduce unnecessary
        # prompt tokens while preserving useful evidence.
        self.max_snippet_length = 600

    # ======================================================
    # COMPLETE WEB ANSWER
    # ======================================================

    def answer(
        self,
        query,
        results,
        intelligence=None,
        grounding=None,
    ):
        """
        Generate a complete web answer.

        This method preserves the existing CLI behavior.
        """

        if not results:
            return "I could not find any relevant web results."

        prompt, source_results = self._build_web_prompt(
            query,
            results,
            intelligence,
            grounding,
        )

        logger.info(
            "Generating web answer for CLI."
        )

        answer_chunks = self.assistant.stream(
            prompt
        )

        answer_parts = []

        for chunk in answer_chunks:
            print(
                chunk,
                end="",
                flush=True,
            )

            answer_parts.append(
                chunk
            )

        print()

        raw_answer = "".join(
            answer_parts
        ).strip()

        answer = self._clean_answer(
            raw_answer
        )

        sources = self._build_sources(
            source_results
        )

        print(
            sources,
            flush=True,
        )

        return answer + sources

    # ======================================================
    # STREAMING WEB ANSWER
    # ======================================================

    def stream_answer(
        self,
        query,
        results,
        intelligence=None,
        grounding=None,
    ):
        """
        Stream a web answer for the browser.

        Measures:
        - Time to first generated chunk.
        - Total model streaming time.
        - Generated character count.

        Unlike answer(), this method NEVER prints generated
        content to the terminal.
        """

        if not results:
            yield (
                "I could not find any relevant web results."
            )
            return

        prompt, source_results = self._build_web_prompt(
            query,
            results,
            intelligence,
            grounding,
        )

        logger.info(
            "Generating streaming web answer."
        )

        stream_start = time.perf_counter()
        first_chunk_time = None
        total_characters = 0
        answer_chunks = []

        for chunk in self.assistant.stream(
            prompt
        ):

            # ----------------------------------------------
            # First chunk timing
            # ----------------------------------------------

            if first_chunk_time is None:

                first_chunk_time = (
                    time.perf_counter()
                    - stream_start
                )

                logger.info(
                    f"Web Stream Timing | "
                    f"First Chunk: "
                    f"{first_chunk_time:.3f}s"
                )

            # ----------------------------------------------
            # Track generated content
            # ----------------------------------------------

            answer_chunks.append(
                chunk
            )

            total_characters += len(
                chunk
            )

            # ----------------------------------------------
            # Send directly to browser
            # ----------------------------------------------

            yield chunk

        # ----------------------------------------------
        # Total streaming timing
        # ----------------------------------------------

        total_stream_time = (
            time.perf_counter()
            - stream_start
        )

        logger.info(
            f"Web Stream Timing | "
            f"Generation: "
            f"{total_stream_time:.3f}s | "
            f"Characters: "
            f"{total_characters}"
        )

        # ----------------------------------------------
        # Application-generated Sources
        # ----------------------------------------------

        sources = self._build_sources(
            source_results
        )

        yield sources

        logger.info(
            "Streaming web answer completed."
        )

    # ======================================================
    # STRUCTURED STREAMING WEB ANSWER
    # ======================================================

    def stream_answer_events(
        self,
        query,
        results,
        intelligence=None,
        grounding=None,
    ):
        """
        Stream structured web events for the browser.

        Event types:
        - status
        - answer
        - sources
        - done

        The answer is streamed first and the application-
        generated sources are emitted after the answer
        finishes.
        """

        if not results:

            yield {
                "type": "answer",
                "content": (
                    "I could not find any relevant web results."
                ),
            }

            yield {
                "type": "done"
            }

            return

        # --------------------------------------------------
        # Build prompt
        # --------------------------------------------------

        prompt, source_results = self._build_web_prompt(
            query,
            results,
            intelligence,
            grounding,
        )

        # --------------------------------------------------
        # Prepare source data
        # --------------------------------------------------

        source_data = []

        grounded_sources = []

        if grounding:
            grounded_sources = grounding.get(
                "grounded_sources",
                [],
            )

        grounded_lookup = {
            source.get("url"): source
            for source in grounded_sources
        }

        for index, result in enumerate(
            source_results,
            start=1,
        ):

            url = result.get(
                "url",
                "",
            )

            grounded_source = grounded_lookup.get(
                url
            )

            citation_id = str(index)

            if grounded_source:

                citation_id = str(
                    grounded_source.get(
                        "citation_id",
                        index,
                    )
                )

            source_data.append(
                {
                    "id": citation_id,
                    "title": result.get(
                        "title",
                        "",
                    ),
                    "url": url,
                }
            )

        # --------------------------------------------------
        # Generation status
        # --------------------------------------------------

        yield {
            "type": "status",
            "content": "Generating answer...",
        }

        logger.info(
            "Web Stream | Answer streaming started."
        )

        # --------------------------------------------------
        # Stream model answer
        # --------------------------------------------------

        stream_start = time.perf_counter()
        first_chunk_time = None
        total_characters = 0

        for chunk in self.assistant.stream(
            prompt
        ):

            # ----------------------------------------------
            # First chunk timing
            # ----------------------------------------------

            if first_chunk_time is None:

                first_chunk_time = (
                    time.perf_counter()
                    - stream_start
                )

                logger.info(
                    f"Web Stream Timing | "
                    f"First Chunk: "
                    f"{first_chunk_time:.3f}s"
                )

            # ----------------------------------------------
            # Track generated characters
            # ----------------------------------------------

            total_characters += len(
                chunk
            )

            # ----------------------------------------------
            # Send answer chunk to browser
            # ----------------------------------------------

            yield {
                "type": "answer",
                "content": chunk,
            }

        # --------------------------------------------------
        # Total streaming timing
        # --------------------------------------------------

        total_stream_time = (
            time.perf_counter()
            - stream_start
        )

        logger.info(
            f"Web Stream Timing | "
            f"Generation: "
            f"{total_stream_time:.3f}s | "
            f"Characters: "
            f"{total_characters}"
        )

        # --------------------------------------------------
        # Send sources AFTER answer
        # --------------------------------------------------

        logger.info(
            f"Web Stream | Sources sent: "
            f"{len(source_data)}"
        )

        yield {
            "type": "sources",
            "sources": source_data,
        }

        # --------------------------------------------------
        # Completion
        # --------------------------------------------------

        yield {
            "type": "done"
        }

        logger.info(
            "Web Stream | Structured stream completed."
        )

    # ======================================================
    # BUILD WEB PROMPT
    # ======================================================

    def _build_web_prompt(
        self,
        query,
        results,
        intelligence=None,
        grounding=None,
    ):
        """
        Build a compact grounded web prompt.

        The prompt is intentionally kept small because
        prompt evaluation happens before Ollama produces
        the first streaming chunk.
        """

        # --------------------------------------------------
        # Grounded Sources
        # --------------------------------------------------

        grounded_sources = []

        if grounding:
            grounded_sources = grounding.get(
                "grounded_sources",
                [],
            )

        grounded_lookup = {
            source["url"]: source
            for source in grounded_sources
        }

        # --------------------------------------------------
        # Select strongest sources
        # --------------------------------------------------

        selected_results = results[
            :self.context_result_limit
        ]

        evidence_parts = []

        for result in selected_results:

            url = result.get(
                "url",
                "",
            )

            grounded_source = grounded_lookup.get(
                url
            )

            citation_id = ""
            source_type = ""
            priority = ""

            if grounded_source:

                citation_id = grounded_source.get(
                    "citation_id",
                    "",
                )

                source_type = grounded_source.get(
                    "source_type",
                    "",
                )

                priority = grounded_source.get(
                    "evidence_priority",
                    "",
                )

            snippet = result.get(
                "snippet",
                "",
            ).strip()

            if len(snippet) > self.max_snippet_length:

                snippet = (
                    snippet[
                        :self.max_snippet_length
                    ]
                    + "..."
                )

            # SourceGrounding already emits bracketed IDs such as "[1]";
            # only add brackets when they are missing (avoids "[[1]]").
            if not citation_id:
                citation_label = ""
            elif str(citation_id).startswith("["):
                citation_label = str(citation_id)
            else:
                citation_label = f"[{citation_id}]"

            metadata = ""

            if source_type:
                metadata += (
                    f"Type: {source_type}. "
                )

            if priority:
                metadata += (
                    f"Priority: {priority}. "
                )

            evidence_parts.append(
                f"{citation_label} "
                f"{metadata}"
                f"Title: {result.get('title', '')}. "
                f"Evidence: {snippet}"
            )

        evidence = "\n\n".join(
            evidence_parts
        )

        # Default so the release decision below also works when no
        # web-intelligence data is available (previously raised
        # UnboundLocalError).
        latest_stable = None

        # --------------------------------------------------
        # Web Intelligence
        # --------------------------------------------------

        intelligence_context = ""

        if intelligence:

            summary = intelligence.get(
                "summary",
                "",
            ).strip()

            if summary:

                intelligence_context += (
                    "\n\n"
                    "Evidence assessment:\n"
                    f"{summary}"
                )

            # ----------------------------------------------
            # Release validation
            # ----------------------------------------------

            release_validation = (
                intelligence.get(
                    "release_validation",
                    {},
                )
            )

            latest_stable = (
                release_validation.get(
                    "latest_stable"
                )
            )

            candidates = (
                release_validation.get(
                    "candidates",
                    [],
                )
            )

            if candidates:

                intelligence_context += (
                    "\n\n"
                    "Release validation:\n"
                )

                for candidate in candidates:

                    intelligence_context += (
                        f"- Version: "
                        f"{candidate['version']} | "
                        f"Status: "
                        f"{candidate['status']} | "
                        f"Source: "
                        f"{candidate['title']}\n"
                    )

        if latest_stable:

            intelligence_context += (
                "\n\n"
                "DETERMINISTIC RELEASE DECISION:\n"
                f"Latest stable version: "
                f"{latest_stable['version']}\n"
                f"Lifecycle status: "
                f"{latest_stable['status']}\n"
                "\n"
                "This version was selected by the "
                "AURORA release validator.\n"
                "Use this version when answering the "
                "latest stable version question.\n"
                "Do not replace it with another version."
            )

        else:

            intelligence_context += (
                "\n\n"
                "DETERMINISTIC RELEASE DECISION:\n"
                "No stable release candidate was validated "
                "from the available web evidence.\n"
                "\n"
                "Do not claim that any unvalidated version "
                "is the latest stable release.\n"
                "Do not convert an Unknown, Release Candidate, "
                "Beta, Alpha, Development, Future, or "
                "Unreleased version into Stable.\n"
                "If the evidence is insufficient, explicitly "
                "state that the latest stable version could "
                "not be reliably verified."
            )
        # --------------------------------------------------
        # Final compact prompt
        # --------------------------------------------------

        prompt = (
            "Answer the user's question using only the "
            "web evidence below.\n\n"

            "Rules:\n"
            "- Use only the provided evidence.\n"
            "- Prefer official or authoritative sources.\n"
            "- For latest/version questions, distinguish "
            "stable releases from RC, beta, development, "
            "future, or unreleased versions.\n"
            "- Treat the release-validation evidence as "
            "authoritative for lifecycle classification.\n"
            "- For latest stable version questions, use the "
            "DETERMINISTIC RELEASE DECISION provided below.\n"
            "- Never independently select a version based only "
            "on its number.\n"
            "- Never replace the validated stable version with "
            "a higher-numbered RC, beta, alpha, development, "
            "future, or unreleased version.\n"
            "- Never describe an RC, beta, development, "
            "or future version as stable.\n"
            "- If no deterministic stable release is provided, "
            "do not infer one from the raw web evidence.\n"
            "- Unknown lifecycle means the release status could "
            "not be established; it must not be treated as Stable.\n"
            "- If sources disagree, state the disagreement.\n"
            "- Use only citation IDs provided in the evidence.\n"
            "- Put citations inline immediately after "
            "supported claims.\n"
            "- Do not invent facts or citations.\n"
            "- Do not output raw URLs.\n"
            "- Do not output a Sources, Citations, References, "
            "or Bibliography section.\n"
            "- Do not reproduce the evidence.\n"
            "- Do not explain reasoning.\n"
            "- Keep the answer concise.\n\n"

            f"User question:\n{query}\n\n"

            f"Web evidence:\n{evidence}"
            f"{intelligence_context}"
        )

        return prompt, results

    # ======================================================
    # BUILD SOURCES
    # ======================================================

    @staticmethod
    def _build_sources(
        source_results,
    ):
        """
        Build the final Sources section generated by
        the application rather than the language model.
        """

        sources = "\n\nSources:\n"

        for index, result in enumerate(
            source_results,
            start=1,
        ):

            sources += (
                f"{index}. {result['title']}\n"
                f"   {result['url']}\n"
            )

        return sources

    # ======================================================
    # ANSWER CLEANUP
    # ======================================================

    @staticmethod
    def _clean_answer(
        answer: str,
    ) -> str:
        """
        Remove internal evidence and source sections that
        the language model may accidentally reproduce.

        The cleanup is intentionally conservative so that
        normal explanatory text and inline citations remain.
        """

        if not answer:
            return answer

        cleaned = answer.strip()

        cleaned = re.sub(
            r"^```(?:text|markdown)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        section_pattern = re.compile(
            r"\n\s*(?:"
            r"sources?"
            r"|citations?"
            r"|references?"
            r"|bibliography"
            r"|source list"
            r"|citation list"
            r")\s*:?\s*.*$",
            flags=re.IGNORECASE | re.DOTALL,
        )

        cleaned = section_pattern.sub(
            "",
            cleaned,
        ).strip()

        metadata_pattern = re.compile(
            r"(?im)^\s*(?:"
            r"title"
            r"|url"
            r"|snippet"
            r"|source type"
            r"|evidence priority"
            r"|evidence"
            r")\s*:\s*.*$"
        )

        cleaned = metadata_pattern.sub(
            "",
            cleaned,
        )

        cleaned = re.sub(
            r"(?m)^\s*\[\d+(?:\s*,\s*\d+)*\]\s*$",
            "",
            cleaned,
        )

        cleaned = re.sub(
            r"(?im)^\s*(?:"
            r"here are the citations"
            r"|here are the sources"
            r"|citations supporting this information"
            r"|sources supporting this information"
            r")\s*:?\s*$",
            "",
            cleaned,
        )

        cleaned = re.sub(
            r"\n{3,}",
            "\n\n",
            cleaned,
        )

        return cleaned.strip()
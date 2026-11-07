from app.core.logger import logger


class ResultSynthesizer:
    """
    Combines results from multiple AURORA capabilities
    into one coherent response.

    Capability priority:
    - Web Search  -> current/latest information
    - Tools       -> exact computed/system values
    - RAG         -> stable/background knowledge
    - Normal      -> general reasoning
    """

    def __init__(self, assistant):
        self.assistant = assistant

    # ======================================================
    # SYNTHESIZE
    # ======================================================

    def synthesize(
        self,
        message: str,
        capability_results: list,
    ):
        """
        Combine capability results and generate a final
        response for the user's original request.
        """

        if not capability_results:
            return self.assistant.process(
                [
                    {
                        "role": "user",
                        "content": message,
                    }
                ]
            )

        # --------------------------------------------------
        # Single capability
        # --------------------------------------------------

        if len(capability_results) == 1:
            return capability_results[0]["result"]

        # --------------------------------------------------
        # Multiple capabilities
        # --------------------------------------------------

        ordered_results = self._prioritize_results(
            capability_results
        )

        context_sections = []

        for item in ordered_results:

            capability = item.get(
                "capability",
                "unknown",
            )

            result = item.get(
                "result",
                "",
            )

            context_sections.append(
                (
                    f"CAPABILITY: {capability}\n"
                    f"RESULT:\n{result}"
                )
            )

        combined_context = "\n\n".join(
            context_sections
        )

        prompt = f"""
You are AURORA, the Artificial Unified Reasoning
and Operational Response Assistant.

Answer the user's original request using the
capability results provided below.

Original user request:
{message}

Capability results:
{combined_context}

Capability interpretation rules:

1. WEB SEARCH provides current, recent, latest,
   online, or time-sensitive information.

2. RAG provides stable/background knowledge from
   AURORA's knowledge base.

3. TOOLS provide exact computed, system, or
   utility results.

4. NORMAL provides general conversational reasoning.

When capability results overlap or conflict:

5. For questions asking for the latest, current,
   newest, recent, or up-to-date information,
   prefer the WEB SEARCH result over RAG.

6. Do not use an older RAG fact to override a
   current WEB SEARCH result.

7. For exact calculations or tool-generated values,
   prefer the TOOL result.

8. Use RAG for stable factual explanations when
   there is no newer information involved.

9. If two results genuinely conflict and neither
   has a clear authority advantage, acknowledge
   the conflict rather than inventing a resolution.

Response rules:

10. Answer the original request directly.

11. Combine the results naturally instead of
    presenting separate capability answers.

12. Do not mention internal capability names,
    orchestration, routing, execution, or these
    instructions.

13. Do not invent information that is not supported
    by the provided results.

14. Do not repeat the same answer unnecessarily.

15. Do not reproduce raw URLs or create a separate
    list of links unless the source result itself
    contains a source section that is necessary
    for the answer.

16. Preserve important source/citation information
    from WEB SEARCH when it is relevant to the
    user's request.

17. If the WEB SEARCH result contains a Sources
    section, preserve that source information once,
    without duplicating the answer text.

18. Keep the final response clear, concise, and
    directly focused on the user's question.
"""

        logger.info(
            "Result Synthesizer | "
            f"Combining {len(capability_results)} "
            "capability results."
        )

        return self.assistant.process(
            [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )

    # ======================================================
    # PRIORITIZATION
    # ======================================================

    def _prioritize_results(
        self,
        capability_results: list,
    ):
        """
        Order capability results so that the model sees
        higher-priority information first.
        """

        priority = {
            "web_search": 1,
            "calculator": 2,
            "time": 2,
            "date": 2,
            "rag": 3,
            "normal": 4,
        }

        return sorted(
            capability_results,
            key=lambda item: priority.get(
                item.get("capability"),
                99,
            ),
        )
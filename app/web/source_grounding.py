import re


class SourceGrounding:
    """
    Maps web evidence to citation-ready source records.
    """

    def __init__(self, max_sources=5):
        self.max_sources = max_sources

        self.temporal_indicators = {
            "latest",
            "current",
            "currently",
            "recent",
            "recently",
            "today",
            "tonight",
            "this week",
            "this month",
            "this year",
            "yesterday",
            "tomorrow",
            "now",
            "up to date",
            "up-to-date",
            "newest",
            "recent developments",
            "what happened",
        }

        self.latest_indicators = {
            "latest",
            "current",
            "currently",
            "newest",
            "most recent",
            "latest stable",
            "current stable",
        }

    def ground(self, query, results):
        """
        Convert ranked web results into structured
        source-grounding records.

        The query is used to determine whether the
        user is asking for current information.
        """

        if not results:
            return {
                "grounded_sources": [],
                "grounding_summary": "",
            }

        grounded_sources = []

        for result in results[:self.max_sources]:

            title = result.get(
                "title",
                "",
            ).strip()

            url = result.get(
                "url",
                "",
            ).strip()

            snippet = result.get(
                "snippet",
                "",
            ).strip()

            if not title or not url:
                continue

            grounded_sources.append(
                {
                    "citation_id": (
                        f"[{len(grounded_sources) + 1}]"
                    ),
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "relevance_score": result.get(
                        "relevance_score",
                        0.0,
                    ),
                    "authority_score": result.get(
                        "authority_score",
                        result.get(
                            "source_authority",
                            0.0,
                        ),
                    ),
                    "freshness_score": result.get(
                        "freshness_score",
                        0.0,
                    ),
                    "combined_score": result.get(
                        "combined_score",
                        0.0,
                    ),
                    "evidence_priority": (
                        self._calculate_evidence_priority(
                            query,
                            result,
                        )
                    ),
                    "source_type": (
                        self._classify_source(
                            result
                        )
                    ),
                    "supports_current_fact": (
                        self._supports_current_fact(
                            query,
                            result,
                        )
                    ),
                }
            )

        summary = self._build_summary(
            grounded_sources
        )

        return {
            "grounded_sources": grounded_sources,
            "grounding_summary": summary,
        }

    def _calculate_evidence_priority(
        self,
        query,
        result,
    ):
        """
        Assign evidence priority based on source
        authority, query intent, and explicit evidence.
        """

        authority = result.get(
            "authority_score",
            result.get(
                "source_authority",
                0.0,
            ),
        )

        query_lower = query.lower()

        is_temporal = self._is_temporal_query(
            query_lower
        )

        supports_current_fact = (
            self._supports_current_fact(
                query,
                result,
            )
        )

        if (
            is_temporal
            and authority >= 1.0
            and supports_current_fact
        ):
            return "HIGH"

        if authority >= 1.0:
            return "AUTHORITATIVE"

        if is_temporal:
            return "MEDIUM"

        return "NORMAL"

    def _supports_current_fact(self, query, result):
        """
        Determine whether the result explicitly supports
        a current/latest claim.

        An authoritative source is not automatically
        evidence for the latest fact. The result must
        contain explicit current/latest wording or point
        to a dedicated latest-release page.
        """

        query_lower = query.lower()

        if not self._is_latest_query(query_lower):
            return False

        title = result.get(
            "title",
            "",
        ).lower()

        url = result.get(
            "url",
            "",
        ).lower()

        snippet = result.get(
            "snippet",
            "",
        ).lower()

        combined_text = (
            f"{title} {url} {snippet}"
        )

        explicit_latest_patterns = [
            r"\blatest\s+stable\b",
            r"\blatest\s+release\b",
            r"\blatest\s+version\b",
            r"\bcurrent\s+stable\b",
            r"\bcurrent\s+release\b",
            r"\bcurrent\s+version\b",
            r"\bnewest\s+release\b",
            r"\bnewest\s+version\b",
            r"\bmost\s+recent\s+release\b",
            r"\bmost\s+recent\s+version\b",
        ]

        for pattern in explicit_latest_patterns:
            if re.search(
                pattern,
                combined_text,
            ):
                return True

        # A dedicated latest-release URL is strong evidence
        # even when the search snippet omits the words
        # "latest stable release".
        if (
            "/downloads/latest" in url
            or url.endswith("/latest")
            or "/latest/" in url
        ):
            return True

        return False

    def _is_temporal_query(self, query):
        """
        Determine whether the query requires
        current or time-sensitive information.
        """

        return any(
            indicator in query
            for indicator in self.temporal_indicators
        )

    def _is_latest_query(self, query):
        """
        Determine whether the user specifically asks
        for the latest/current version or release.
        """

        return any(
            indicator in query
            for indicator in self.latest_indicators
        )

    def _classify_source(self, result):
        """
        Classify the source based on its authority.
        """

        authority = result.get(
            "authority_score",
            result.get(
                "source_authority",
                0.0,
            ),
        )

        if authority >= 1.0:
            return "Official / Authoritative"

        return "Secondary Source"

    def _build_summary(self, grounded_sources):
        """
        Build a compact description of the
        available citation sources.
        """

        if not grounded_sources:
            return "No grounded sources are available."

        high_priority = sum(
            1
            for source in grounded_sources
            if source["evidence_priority"] == "HIGH"
        )

        current_fact_sources = sum(
            1
            for source in grounded_sources
            if source["supports_current_fact"]
        )

        return (
            f"{len(grounded_sources)} source(s) are "
            f"available for citation. "
            f"{high_priority} source(s) have high "
            "evidence priority. "
            f"{current_fact_sources} source(s) explicitly "
            "support the requested current fact."
        )
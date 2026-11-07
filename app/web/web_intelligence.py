from app.web.web_release_validator import (
    WebReleaseValidator
)

from app.core.logger import logger


class WebIntelligence:
    """
    Analyzes processed web search results and prepares
    structured evidence for answer generation.
    """

    def __init__(self, max_evidence=3):
        self.max_evidence = max_evidence
        self.release_validator = (
            WebReleaseValidator()
        )

    def analyze(self, results):
        """
        Analyze ranked web search results.

        Returns structured information containing:
        - strongest evidence
        - supporting sources
        - conflicting sources
        - evidence summary
        """

        if not results:
            return {
                "evidence": [],
                "supporting_sources": [],
                "conflicting_sources": [],
                "summary": "",
            }

        evidence = self._extract_evidence(results)

        supporting_sources = self._find_supporting_sources(
            evidence
        )

        conflicting_sources = self._find_conflicting_sources(
            evidence
        )

        summary = self._build_summary(
            evidence,
            supporting_sources,
            conflicting_sources,
        )

        release_validation = (
            self.release_validator.validate(
                results
            )
        )

        latest_stable = (
            release_validation.get(
                "latest_stable"
            )
        )

        if latest_stable:

            logger.info(
                f"Web Release Validation | "
                f"Candidates: "
                f"{len(release_validation.get('candidates', []))} | "
                f"Latest Stable: "
                f"{latest_stable['version']} | "
                f"Status: "
                f"{latest_stable['status']}"
            )

        else:

            logger.info(
                "Web Release Validation | "
                "No stable candidate detected."
            )

        return {
            "evidence": evidence,
            "supporting_sources": supporting_sources,
            "conflicting_sources": conflicting_sources,
            "summary": summary,
            "release_validation": release_validation,
        }

    def _extract_evidence(self, results):
        """
        Select the strongest available results as evidence.
        """

        evidence = []

        for result in results[:self.max_evidence]:
            evidence.append(
                {
                    "title": result.get(
                        "title",
                        "",
                    ),
                    "url": result.get(
                        "url",
                        "",
                    ),
                    "snippet": result.get(
                        "snippet",
                        "",
                    ),
                    "authority_score": result.get(
                        "authority_score",
                        result.get(
                            "source_authority",
                            0.0,
                        ),
                    ),
                    "relevance_score": result.get(
                        "relevance_score",
                        0.0,
                    ),
                    "freshness_score": result.get(
                        "freshness_score",
                        0.0,
                    ),
                    "combined_score": result.get(
                        "combined_score",
                        0.0,
                    ),
                }
            )

        return evidence

    def _find_supporting_sources(self, evidence):
        """
        Detect sources that share meaningful terms.

        Shared terms provide a lightweight indication
        that multiple sources discuss similar evidence.
        """

        supporting = []

        token_sets = []

        for item in evidence:
            tokens = self._tokenize(
                item["snippet"]
            )
            token_sets.append(tokens)

        for index in range(len(evidence)):
            for other_index in range(
                index + 1,
                len(evidence),
            ):
                shared = (
                    token_sets[index]
                    & token_sets[other_index]
                )

                if len(shared) >= 3:
                    supporting.append(
                        {
                            "source_a": evidence[index]["title"],
                            "source_b": evidence[
                                other_index
                            ]["title"],
                            "shared_terms": sorted(shared),
                        }
                    )

        return supporting

    def _find_conflicting_sources(self, evidence):
        """
        Detect obvious contradiction indicators.

        This is intentionally conservative. It does not
        claim two sources disagree merely because their
        wording differs.
        """

        conflict_words = {
            "not",
            "never",
            "no",
            "false",
            "incorrect",
            "unavailable",
            "discontinued",
            "deprecated",
        }

        conflicting = []

        for index, item in enumerate(evidence):
            tokens_a = self._tokenize(
                item["snippet"]
            )

            if not tokens_a & conflict_words:
                continue

            for other_index in range(
                index + 1,
                len(evidence),
            ):
                tokens_b = self._tokenize(
                    evidence[other_index]["snippet"]
                )

                if tokens_b & conflict_words:
                    continue

                shared = tokens_a & tokens_b

                if len(shared) >= 3:
                    conflicting.append(
                        {
                            "source_a": item["title"],
                            "source_b": evidence[
                                other_index
                            ]["title"],
                            "shared_terms": sorted(shared),
                        }
                    )

        return conflicting

    def _build_summary(
        self,
        evidence,
        supporting_sources,
        conflicting_sources,
    ):
        """
        Build a compact textual description of the
        available web evidence.
        """

        if not evidence:
            return "No web evidence is available."

        summary_parts = [
            f"{len(evidence)} strong web sources "
            "were selected for analysis."
        ]

        if supporting_sources:
            summary_parts.append(
                f"{len(supporting_sources)} source pair(s) "
                "contain overlapping evidence."
            )

        if conflicting_sources:
            summary_parts.append(
                f"{len(conflicting_sources)} possible "
                "conflicting source pair(s) were detected."
            )

        if not supporting_sources and not conflicting_sources:
            summary_parts.append(
                "No strong cross-source agreement or "
                "conflict was detected."
            )

        return " ".join(summary_parts)

    def _tokenize(self, text):
        """
        Convert text into normalized terms.
        """

        tokens = set(
            token.lower().strip(
                ".,!?;:()[]{}\"'"
            )
            for token in text.split()
        )

        return {
            token
            for token in tokens
            if len(token) >= 4
        }
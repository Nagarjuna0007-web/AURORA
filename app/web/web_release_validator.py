import re
from app.core.logger import logger

class WebReleaseValidator:
    """
    Validates software release/version information found
    in web search results.

    The validator is generic and does not contain
    product-specific version numbers.

    Supported lifecycle states:
    - Stable
    - Release Candidate
    - Beta
    - Alpha
    - Development
    - Future / Unreleased
    - Unknown
    """

    VERSION_PATTERN = re.compile(
        r"\b"
        r"v?"
        r"(\d+)"
        r"\."
        r"(\d+)"
        r"(?:"
        r"\."
        r"(\d+)"
        r")?"
        r"(?:"
        r"[-_ ]?"
        r"(alpha|beta|rc|dev)"
        r"(?:[._-]?(\d+))?"
        r")?"
        r"\b",
        re.IGNORECASE,
    )

    LIFECYCLE_PATTERNS = {
        "Release Candidate": (
            "release candidate",
            "rc",
            "rc1",
            "rc2",
            "rc3",
        ),
        "Beta": (
            "beta",
            "beta release",
            "beta version",
        ),
        "Alpha": (
            "alpha",
            "alpha release",
            "alpha version",
        ),
        "Development": (
            "development",
            "develop",
            "dev version",
            "development version",
            "main branch",
            "nightly",
            "unstable",
            "pre-release",
            "prerelease",
        ),
        "Future / Unreleased": (
            "future release",
            "future version",
            "not yet released",
            "not released",
            "upcoming release",
            "upcoming version",
            "unreleased",
        ),
    }

    def validate(self, results):
        """
        Analyze web search results and extract version
        candidates with their lifecycle status.
        """

        candidates = []

        for result in results or []:

            title = result.get(
                "title",
                "",
            )

            snippet = result.get(
                "snippet",
                "",
            )

            text = f"{title} {snippet}"

            versions = self._extract_versions(
                text
            )

            for version in versions:

                status = self._classify_status(
                    version,
                    text,
                )

                candidates.append(
                    {
                        "version": version,
                        "status": status,
                        "title": title,
                        "url": result.get(
                            "url",
                            "",
                        ),
                    }
                )

        candidates = self._deduplicate(
            candidates
        )

        unknown_candidates = [
            candidate
            for candidate in candidates
            if candidate["status"] == "Unknown"
        ]

        if unknown_candidates:

            logger.info(
                f"Web Release Validation | "
                f"Unknown lifecycle candidates: "
                f"{len(unknown_candidates)}"
            )

        stable_candidates = [
            candidate
            for candidate in candidates
            if candidate["status"] == "Stable"
        ]

        prerelease_candidates = [
            candidate
            for candidate in candidates
            if candidate["status"] != "Stable"
        ]

        result = {
            "candidates": candidates,
            "stable_candidates": stable_candidates,
            "prerelease_candidates": prerelease_candidates,
            "summary": self._build_summary(
                candidates
            ),
        }

        result["latest_stable"] = (
            self.select_latest_stable(
                result
            )
        )

        return result

    # ======================================================
    # VERSION EXTRACTION
    # ======================================================

    def _extract_versions(self, text):
        versions = []

        for match in self.VERSION_PATTERN.finditer(
            text
        ):

            major = match.group(1)
            minor = match.group(2)
            patch = match.group(3)

            suffix = match.group(4)
            suffix_number = match.group(5)

            version = (
                f"{major}.{minor}"
            )

            if patch is not None:
                version += f".{patch}"

            if suffix:

                version += suffix.lower()

                if suffix_number:
                    version += suffix_number

            if version not in versions:
                versions.append(version)

        return versions

    # ======================================================
    # LIFECYCLE CLASSIFICATION
    # ======================================================

    def _classify_status(
        self,
        version,
        text,
    ):
        normalized = text.lower()

        version_lower = version.lower()

        # --------------------------------------------------
        # Explicit version suffixes
        # --------------------------------------------------

        if "rc" in version_lower:
            return "Release Candidate"

        if "alpha" in version_lower:
            return "Alpha"

        if "beta" in version_lower:
            return "Beta"

        if "dev" in version_lower:
            return "Development"

        # --------------------------------------------------
        # Explicit lifecycle wording
        # --------------------------------------------------

        for status, indicators in (
            self.LIFECYCLE_PATTERNS.items()
        ):

            for indicator in indicators:

                if indicator in normalized:
                    return status

        # --------------------------------------------------
        # Explicit stable wording
        # --------------------------------------------------

        stable_indicators = (
            "stable release",
            "latest stable",
            "stable version",
            "stable maintenance release",
            "official release",
            "final release",
            "released",
            "release",
        )

        for indicator in stable_indicators:

            if indicator in normalized:
                return "Stable"

        # --------------------------------------------------
        # Unknown lifecycle
        # --------------------------------------------------

        return "Unknown"

    # ======================================================
    # STABLE CANDIDATE SELECTION
    # ======================================================

    def select_latest_stable(
        self,
        validation_result,
    ):
        """
        Select the highest stable version candidate.

        Pre-release and development versions are never
        selected as the latest stable version.
        """

        stable_candidates = validation_result.get(
            "stable_candidates",
            [],
        )

        if not stable_candidates:
            return None

        ranked = sorted(
            stable_candidates,
            key=lambda candidate: self._version_key(
                candidate["version"]
            ),
            reverse=True,
        )

        return ranked[0]

    # ======================================================
    # VERSION COMPARISON
    # ======================================================

    @staticmethod
    def _version_key(version):
        """
        Convert a version string into a comparable tuple.

        Examples:

        3.14.7     -> (3, 14, 7)
        3.14       -> (3, 14, 0)
        24.6.0     -> (24, 6, 0)
        """

        match = re.match(
            r"^(\d+)\.(\d+)"
            r"(?:\.(\d+))?",
            version,
        )

        if not match:
            return (
                0,
                0,
                0,
            )

        major = int(
            match.group(1)
        )

        minor = int(
            match.group(2)
        )

        patch = int(
            match.group(3)
            or 0
        )

        return (
            major,
            minor,
            patch,
        )

    # ======================================================
    # DEDUPLICATION
    # ======================================================

    @staticmethod
    def _deduplicate(
        candidates,
    ):
        unique = []
        seen = set()

        for candidate in candidates:

            key = (
                candidate["version"],
                candidate["status"],
                candidate["url"],
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(candidate)

        return unique

    # ======================================================
    # SUMMARY
    # ======================================================

    @staticmethod
    def _build_summary(
        candidates,
    ):
        if not candidates:
            return (
                "No recognizable release versions "
                "were found in the web evidence."
            )

        stable = [
            item
            for item in candidates
            if item["status"] == "Stable"
        ]

        prerelease = [
            item
            for item in candidates
            if item["status"] != "Stable"
        ]

        parts = [
            f"{len(candidates)} version candidate(s) "
            "were detected."
        ]

        if stable:
            parts.append(
                f"{len(stable)} candidate(s) "
                "are classified as stable."
            )

        if prerelease:
            parts.append(
                f"{len(prerelease)} candidate(s) "
                "are classified as pre-release, "
                "development, or unreleased."
            )

        return " ".join(parts)